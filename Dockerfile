# Multi-stage build: smaller, more secure final image
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

# Run as non-root user (security best practice, checked by container scanning)
RUN useradd -m appuser
WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

USER appuser

ARG APP_VERSION=0.0.0-dev
ENV APP_VERSION=${APP_VERSION}

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "2"]
