#!/bin/bash
set -euo pipefail

# Параметры: ./deploy.sh <image_name> <image_tag>
IMAGE_NAME="${1:-ghcr.io/only-hell/catty-reminders-app}"
IMAGE_TAG="${2:-latest}"
IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

CONTAINER_NAME="catty-app"
HOST_PORT="8181"
GUEST_PORT="8181"

echo "--- Deployment started ---"
echo "Image: ${IMAGE}"

# 1. Останавливаем старый systemd-сервис из Лабы 2 (если он ещё жив)
if systemctl is-active --quiet catty-app 2>/dev/null; then
    echo ">> Stopping legacy systemd service catty-app"
    sudo systemctl stop catty-app
    sudo systemctl disable catty-app || true
fi

# 2. Освобождаем порт на всякий случай
sudo fuser -k "${HOST_PORT}/tcp" 2>/dev/null || true

# 3. Pull нового образа
echo ">> Pulling image"
docker pull "${IMAGE}"

# 4. Останавливаем и удаляем старый контейнер
echo ">> Removing old container"
docker stop "${CONTAINER_NAME}" 2>/dev/null || true
docker rm   "${CONTAINER_NAME}" 2>/dev/null || true

# 5. Запускаем новый контейнер
echo ">> Starting new container"
docker run -d \
    --name "${CONTAINER_NAME}" \
    --restart unless-stopped \
    -p "${HOST_PORT}:${GUEST_PORT}" \
    -e DEPLOY_REF="${IMAGE_TAG}" \
    "${IMAGE}"

# 6. Проверка
sleep 4
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "✅ Deployment OK: ${IMAGE_TAG}"
else
    echo "❌ Container not running, logs:"
    docker logs "${CONTAINER_NAME}" || true
    exit 1
fi
