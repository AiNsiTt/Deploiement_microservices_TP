# Order Service Dockerfile
FROM python:3.11-slim

LABEL maintainer="Quentin Chaillou"
LABEL service="notification-service"

ENV PYTHONUNBUFFERED=1
RUN useradd -m -u 1000 appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
RUN chown -R appuser:appuser /app

USER appuser
EXPOSE 8006

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8006/health')" || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8006"]
