#!/bin/bash

set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" ]]; then
    echo "CRITICAL: Missing required variables."
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"

REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

echo "Deploying via Docker Compose..."
echo "Release hash: $RELEASE_HASH"
echo "Repository: $REPO_LOWER"

ssh -p "$TARGET_PORT" \
    -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT

set -e

export REPO_LOWER="${REPO_LOWER}"
export RELEASE_HASH="${RELEASE_HASH}"

export MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}"
export MYSQL_USER="${MYSQL_USER}"
export MYSQL_PASSWORD="${MYSQL_PASSWORD}"

APP_DIR="\$HOME/catty-reminders-app"

echo "--> Creating application directory if needed"
mkdir -p \$APP_DIR

echo "--> Entering app directory"
cd \$APP_DIR

echo "--> Current directory:"
pwd

echo "--> Docker Compose file:"
ls -la

echo "--> Docker version:"
docker --version

echo "--> Docker Compose version:"
docker-compose --version

echo "--> Logging into GHCR"
echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USER}" --password-stdin

echo "--> Pulling exact release image"
docker pull ghcr.io/${REPO_LOWER}:${RELEASE_HASH}

echo "--> Stopping old containers"
docker-compose down || true

echo "--> Pulling compose images"
docker-compose pull

echo "--> Starting database"
docker-compose up -d db

echo "--> Waiting for database startup..."
sleep 10

echo "--> Starting backend"
docker-compose up -d --force-recreate catty_backend

echo "--> Running containers:"
docker ps

echo "--> Backend logs:"
docker logs catty_backend --tail 50 || true

echo "--> Cleaning unused images"
docker image prune -af || true

echo "--> Deployment finished successfully"

REMOTE_SCRIPT
