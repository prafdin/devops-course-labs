FROM python:3.11-slim

WORKDIR /opt/catty

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG DEPLOY_REF
ENV DEPLOY_REF=$DEPLOY_REF

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
