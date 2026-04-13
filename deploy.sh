#!/bin/bash
cd /home/vboxuser/catty-reminders-app
COMMIT_SHA=$1
if [ -z "$COMMIT_SHA" ]; then
  COMMIT_SHA=$(git rev-parse HEAD)
fi
echo "DEPLOY_REF=$COMMIT_SHA" > .env
docker stop lab2-app 2>/dev/null || true
docker rm -f lab2-app 2>/dev/null || true
docker build -t lab2-app-image .
docker run -d --name lab2-app --restart always -p 8181:8181 --env-file .env lab2-app-image
