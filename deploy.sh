#!/bin/bash
set -e

SHA=$1
IMAGE=ghcr.io/only-hell/catty-reminders-app:$SHA

echo "Deploying with SHA: $SHA"
echo "Image: $IMAGE"

cd ~/catty-reminders-app

# Останавливаем и удаляем старые контейнеры
docker compose down --remove-orphans

# Обновляем IMAGE и DEPLOY_REF в .env
sed -i "s|^IMAGE=.*|IMAGE=$IMAGE|" .env
sed -i "s|^DEPLOY_REF=.*|DEPLOY_REF=$SHA|" .env

# Запускаем новые контейнеры
docker compose up -d --pull always
