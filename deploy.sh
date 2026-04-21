#!/bin/bash
set -e

DEPLOY_SHA=$1

if [ -z "$DEPLOY_SHA" ]; then
  echo "Error: SHA not provided"
  exit 1
fi

IMAGE="ghcr.io/only-hell/catty-reminders-app:${DEPLOY_SHA}"

echo "Deploying with SHA: ${DEPLOY_SHA}"
echo "Image: ${IMAGE}"

cd ~/catty-reminders-app

# Login to GHCR
echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USER}" --password-stdin

# Обновляем IMAGE и DEPLOY_REF в .env
sed -i "s|^IMAGE=.*|IMAGE=${IMAGE}|" .env
sed -i "s|^DEPLOY_REF=.*|DEPLOY_REF=${DEPLOY_SHA}|" .env

# Останавливаем старые контейнеры
docker compose down --remove-orphans

# Запускаем новые контейнеры
docker compose up -d --pull always