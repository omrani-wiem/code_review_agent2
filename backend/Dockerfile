FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \ 
    pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim  AS runtime

RUN useradd --create-home appuser
WORKDIR /app

COPY  --from=builder /install /usr/local

COPY --chown=appuser:appuser . .

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000
 
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
 

CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]
 
