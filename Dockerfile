FROM python:3.11-slim

ARG DEPLOY_REF
ENV DEPLOY_REF=$DEPLOY_REF

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN playwright install chromium

COPY . .

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
