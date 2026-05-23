FROM python:3.12-slim

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
COPY config.json .

# Ждем базу перед стартом
CMD sh -c "while ! nc -z db 3306; do echo 'Waiting for DB...'; sleep 2; done; uvicorn app.main:app --host 0.0.0.0 --port 8181"
