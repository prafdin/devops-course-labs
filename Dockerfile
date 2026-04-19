FROM python:3.11-slim

WORKDIR /catty

COPY . .

RUN pip install -r requirements.txt

ARG COMMIT_SHA=manual-test
ENV DEPLOY_REF=$COMMIT_SHA

EXPOSE 8181

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
