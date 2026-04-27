FROM python:3.12

ARG DEPLOY_REF=NA

ENV DEPLOY_REF=${DEPLOY_REF}

WORKDIR /catty-reminders-app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
EXPOSE 8181
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
