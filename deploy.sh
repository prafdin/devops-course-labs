#!/bin/bash

echo "======================================"
echo "Начинаем деплой сервиса..."
echo "======================================"

DEPLOY_REF=$1
GITHUB_TOKEN=$2

IMAGE="ghcr.io/barnaeva/catty-reminders-app:$DEPLOY_REF"

echo "$GITHUB_TOKEN" | docker login ghcr.io -u barnaeva --password-stdin

docker pull $IMAGE

docker stop catty-reminders-app 2>/dev/null || true
docker rm catty-reminders-app 2>/dev/null || true

docker run -d \
    --name catty-reminders-app \
    -p 8181:8181 \
    --restart unless-stopped \
    -e DEPLOY_REF=$DEPLOY_REF \
    $IMAGE

echo "Деплой завершен!"