#!/bin/bash
set -e

IMAGE_FULL="$1:$2"
CONTAINER_NAME="catty-reminders-app"

echo "Деплой образа: $IMAGE_FULL"

echo "Очистка..."
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

echo "Скачиваем..."
docker pull $IMAGE_FULL

echo "Запуск..."
docker run -d \
    -p 8181:8181 \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    $IMAGE_FULL

echo "Готово!"
