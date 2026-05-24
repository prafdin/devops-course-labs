#!/bin/bash
set -e

REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

APP_DIR="/home/qzm/Desktop/catty-reminders-app"

echo "Deploying to $APP_DIR..."

ssh -p "${SERVER_PORT:-22}" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" << REMOTE_SCRIPT
    set -e
    cd ${APP_DIR}
    
    echo "REPO_LOWER=${REPO_LOWER}" > .env
    echo "RELEASE_HASH=${RELEASE_HASH}" >> .env

    echo "--> Stopping stack"
    docker compose down --remove-orphans

    echo "--> Pulling image"
    docker compose pull

    echo "--> Starting stack"
    docker compose up -d

    echo "--> Cleanup"
    docker image prune -af || true
REMOTE_SCRIPT
