#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" ]]; then
    echo "CRITICAL: Missing required variables."
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

APP_DIR="/home/vboxuser/catty-reminders-app"

echo "Deploying to ${SERVER_HOST}..."

ssh -p "$TARGET_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT
set -e

APP_DIR="${APP_DIR}"

mkdir -p \$APP_DIR
cd \$APP_DIR

echo "REPO_LOWER=${REPO_LOWER}" > .env
echo "RELEASE_HASH=${RELEASE_HASH}" >> .env

echo "--> Current env:"
cat .env

echo "--> Stopping old containers"
docker compose down || true

echo "--> Pulling latest image"
docker compose pull

echo "--> Starting containers"
docker compose up -d

echo "--> Cleaning old images"
docker image prune -af || true

echo "--> Deployment finished"
REMOTE_SCRIPT
