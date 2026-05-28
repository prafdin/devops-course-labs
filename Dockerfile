FROM python:3.12-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ARG DEPLOY_REF
ENV DEPLOY_REF=${DEPLOY_REF}
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
COPY config.json .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
