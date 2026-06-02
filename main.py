from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import os
import logging

from crew import run_review

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=" Code Review API",
    description="4-agent AI pipeline: Bug Detector → Reviewer → Corrector → Test Engineer",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["Get", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],  
)

class ReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to review")
    language: str = Field(default="python", description="Programming language hint")


class ReviewResponse(BaseModel):
    language: str
    bugs: str
    review: str
    corrected_code: str
    tests: str
    final_summary: str



@app.get("/")
def root():
    return {
       "service": " Code Review",
        "version": "1.0.0",
        "agents": ["Bug Detector", "Code Reviewer", "Code Corrector", "Test Engineer"],
        "docs": "/docs",
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0"
    }



@app.post("/review", response_model=ReviewResponse)
def review_code(body: ReviewRequest):
    if not os.getenv("open_ai_key"):
        raise HTTPEXCEPTION(
            status_code=500,
        )
    
    logger.info(f"Starting review for {len(body.code)} chars of {body.language} code")


    try:
        result = run_review(body.code)
    except Exception as exc:
         logger.error(f"CrewAI pipeline failed: {exc}", exc_info=True)
         raise HTTPException(status_code=500, detail=f"Review pipeline error: {str(exc)}")
    

    return ReviewResponse(
        language=body.language,
        bugs=result["bugs"],
        review=result["review"],
        corrected_code=result["corrected"],
        tests=result["tests"],
        final_summary=result["final_output"],
    )


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )