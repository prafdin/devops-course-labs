FROM python:3.12

WORKDIR /catty-reminders-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ARG DEPLOY_REF="NA"
ENV DEPLOY_REF=${DEPLOY_REF}

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
