FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV PORT=8080
ENV OTEL_SERVICE_NAME=service-b
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

