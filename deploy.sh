#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" || -z "$REPO_NAME" ]]; then
    echo "CRITICAL: Missing required variables."
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')
APP_DIR="/home/qzm/Desktop/catty-reminders-app"

echo "Deploying via Docker Compose..."

ssh -p "$TARGET_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" << REMOTE_SCRIPT
    set -e

    cd ${APP_DIR}

    echo "--> Stopping old compose stack"
    docker compose down --remove-orphans

    echo "--> Pulling latest images"
    REPO_LOWER=${REPO_LOWER} RELEASE_HASH=${RELEASE_HASH} docker compose pull
    
    echo "--> Starting containers"
    REPO_LOWER=${REPO_LOWER} RELEASE_HASH=${RELEASE_HASH} docker compose up -d

    echo "--> Cleaning up old unused images"
    docker image prune -af || true
    
    echo "--> Deployment finished successfully"
REMOTE_SCRIPT
