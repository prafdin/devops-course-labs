#!/bin/bash

echo "Запуск деплоя catty-reminders-app..."
echo "======================================"

DEPLOY_REF=$1
IMAGE_NAME="ghcr.io/deemeed/catty-reminders-app:$DEPLOY_REF"

echo "Текущий SHA ветки: $DEPLOY_REF"

docker pull $IMAGE_NAME

docker stop catty-container 2>/dev/null || true
docker rm catty-container 2>/dev/null || true

docker run -d \
    --name catty-container \
    -p 8181:8181 \
    --restart unless-stopped \
    -e DEPLOY_REF=$DEPLOY_REF \
    $IMAGE_NAME

echo "Деплой успешно завершен!"