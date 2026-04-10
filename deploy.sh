#!/bin/bash
set -e

IMAGE_NAME="$1"
DEPLOY_REF="$2"
IMAGE_FULL="${IMAGE_NAME}:${DEPLOY_REF}"

APP_DIR="/home/kirill/desktop/devops"
ENV_FILE="$APP_DIR/.env.deploy"
CONTAINER_NAME="catty-reminders-app"
PORT=8181

echo "Deploying: $IMAGE_FULL"
echo "DEPLOY_REF: $DEPLOY_REF"

echo "Cleaning..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

echo "Pulling..."
docker pull "$IMAGE_FULL"

printf 'DEPLOY_REF=%s\n' "$DEPLOY_REF" > "$ENV_FILE"
echo "Saved DEPLOY_REF=$DEPLOY_REF to $ENV_FILE"

echo "Starting container..."
docker run -d \
    -p "$PORT":"$PORT" \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    "$IMAGE_FULL"

echo "Deploy complete!"
