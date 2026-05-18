#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/home/kali/catty-reminders-app"
echo "Deploying multi-container stack into '$APP_DIR'"
cd "$APP_DIR"

# 1. Сбрасываем локальные изменения на Kali и подтягиваем свежий коммит/docker-compose.yaml
git fetch origin lab4
git checkout lab4
git reset --hard origin/lab4

# 2. Авторизуемся в реестре GitHub Packages (ghcr.io)
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

# 3. Останавливаем текущий стек (если он запущен)
docker compose down --remove-orphans

# 4. Скачиваем свежие образы из GHCR и запускаем стек в фоновом режиме
export DEPLOY_REF="$DEPLOY_REF"
docker compose pull
docker compose up -d

echo "Docker Compose deployment completed successfully!"
