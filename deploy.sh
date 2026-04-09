#!/bin/bash
set -e

# === Параметры ===
APP_DIR="/home/kirill/desktop/devops"
ENV_FILE="$APP_DIR/.env.deploy"
IMAGE_FULL="$1:$2"
CONTAINER_NAME="catty-reminders-app"
PORT=8181

echo "Deploying: $IMAGE_FULL"

echo "Cleaning..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

sudo fuser -k "$PORT/tcp" 2>/dev/null || true

echo "Pulling..."
docker pull "$IMAGE_FULL"

DEPLOY_REF="$2"
printf 'DEPLOY_REF=%s\n' "$DEPLOY_REF" > "$ENV_FILE"
echo "Saved DEPLOY_REF=$DEPLOY_REF to $ENV_FILE"

echo "tarting container..."
docker run -d \
    -p "$PORT":"$PORT" \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -e DEPLOY_REF="$DEPLOY_REF" \
    "$IMAGE_FULL"

echo "Deploy complete!"
