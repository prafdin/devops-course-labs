#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/home/kali/catty-reminders-app"
echo "Deploying via Docker into '$APP_DIR'"
cd "$APP_DIR"

# Авторизация в реестре через переданный токен
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

echo "Pulling Docker image: $IMAGE"
docker pull "$IMAGE"

echo "Stopping old container..."
docker stop catty-test || true
docker rm catty-test || true

echo "Starting new Docker container..."
docker run -d \
  -p 8181:8181 \
  --name catty-test \
  --restart unless-stopped \
  -e DEPLOY_REF="$DEPLOY_REF" \
  "$IMAGE"

echo "Docker deployment completed successfully!"
