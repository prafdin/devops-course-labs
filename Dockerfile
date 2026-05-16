FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
COPY inputs.json .

ARG DEPLOY_REF=NA
ENV DEPLOY_REF=${DEPLOY_REF}

EXPOSE 8181
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
