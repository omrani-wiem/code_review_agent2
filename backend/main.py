import os
import uuid
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from cache import get_cached, set_cached
from crew import run_review

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Vérifie la config critique avant d'accepter des requêtes."""
    missing = []
    if not os.getenv("GROQ_API_KEY"):
        missing.append("GROQ_API_KEY")
    if not os.getenv("API_KEY"):
        missing.append("API_KEY")
    if missing:
        raise RuntimeError(
            f"Variables d'environnement manquantes : {', '.join(missing)}"
        )
    logger.info(" Configuration validée — API prête.")
    yield
    logger.info(" Arrêt de l'API.")



app = FastAPI(
    title="Code Review API",
    description="4-agent AI pipeline: Bug Detector → Reviewer → Corrector → Test Engineer",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def require_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)):
    if not api_key:
        raise HTTPException(status_code=401, detail="Header X-API-Key manquant.")
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Clé API invalide.")
    return api_key



jobs: dict[str, dict] = {}

class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Code source à analyser")
    language: str = Field(default="python", description="Langage de programmation")


class ReviewResponse(BaseModel):
    language: str
    bugs: str
    review: str
    corrected_code: str
    tests: str
    final_summary: str


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[ReviewResponse] = None
    error: Optional[str] = None


@app.get("/")
def root():
    return {
        "service": "Code Review API",
        "version": "2.0.0",
        "agents": ["Bug Detector", "Code Reviewer", "Code Corrector", "Test Engineer"],
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/review", response_model=ReviewResponse, dependencies=[Depends(require_api_key)])
def review_code(body: ReviewRequest):
    """Review synchrone — le client attend la fin du pipeline."""
    logger.info(" Review sync — %d chars [%s]", len(body.code), body.language)

    cached = get_cached(body.code)
    if cached:
        logger.info(" Résultat servi depuis le cache.")
        return ReviewResponse(
            language=body.language,
            bugs=cached["bugs"],
            review=cached["review"],
            corrected_code=cached["corrected"],
            tests=cached["tests"],
            final_summary=cached["final_output"],
        )

    try:
        result = run_review(body.code)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Pipeline timeout.")
    except Exception as exc:
        logger.error(" Pipeline error : %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur pipeline : {exc}")

    set_cached(body.code, result)

    return ReviewResponse(
        language=body.language,
        bugs=result["bugs"],
        review=result["review"],
        corrected_code=result["corrected"],
        tests=result["tests"],
        final_summary=result["final_output"],
    )


def _run_pipeline_job(job_id: str, code: str, language: str):
    """Exécutée en arrière-plan — met à jour jobs[job_id]."""
    jobs[job_id]["status"] = "running"
    logger.info(" Job %s démarré.", job_id)

    try:
        cached = get_cached(code)
        if cached:
            result_data = cached
        else:
            result_data = run_review(code)
            set_cached(code, result_data)

        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = ReviewResponse(
            language=language,
            bugs=result_data["bugs"],
            review=result_data["review"],
            corrected_code=result_data["corrected"],
            tests=result_data["tests"],
            final_summary=result_data["final_output"],
        )
        logger.info(" Job %s terminé.", job_id)

    except Exception as exc:
        logger.error(" Job %s échoué : %s", job_id, exc, exc_info=True)
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(exc)


@app.post("/review/async", response_model=JobResponse, status_code=202, dependencies=[Depends(require_api_key)])
def review_code_async(body: ReviewRequest, background_tasks: BackgroundTasks):
    """Soumet un job async — retourne job_id immédiatement."""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "result": None, "error": None}
    background_tasks.add_task(_run_pipeline_job, job_id, body.code, body.language)
    logger.info(" Job %s soumis.", job_id)
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Job soumis. Utilisez GET /review/status/{job_id} pour suivre.",
    )


@app.get("/review/status/{job_id}", response_model=JobStatusResponse, dependencies=[Depends(require_api_key)])
def get_job_status(job_id: str):
    """Retourne l'état d'un job async."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' introuvable.")
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        result=job.get("result"),
        error=job.get("error"),
    )



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )