#!/bin/bash
set -e

APP_DIR="/home/vboxuser/catty-reminders-app"
TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

echo "Deploying..."

ssh -p "$TARGET_PORT" \
  -o StrictHostKeyChecking=no \
  "${SERVER_USER}@${SERVER_HOST}" << EOF

set -e

cd $APP_DIR

echo "RELEASE_HASH=$RELEASE_HASH" > .env
echo "REPO_LOWER=$REPO_LOWER" >> .env

docker-compose --env-file .env down || true
docker-compose --env-file .env pull
docker-compose --env-file .env up -d --force-recreate

docker image prune -af || true
docker ps

EOF
