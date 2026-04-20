#!/bin/bash
set -e

# Берем SHA коммита
COMMIT_SHA=${1:-$(git rev-parse HEAD)}
export DEPLOY_REF=$COMMIT_SHA

echo "🚀 Deploying Lab 4 with SHA: $DEPLOY_REF"

# Чистим порт и старье
sudo fuser -k 8181/tcp || true
docker compose down || true

# Собираем и поднимаем
docker compose build
docker compose up -d

echo "⏳ Waiting for app startup..."
sleep 10
docker compose ps