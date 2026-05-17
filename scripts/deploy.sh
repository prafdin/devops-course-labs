#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" ]]; then
    echo "CRITICAL: Missing required variables."
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

APP_DIR="/home/vboxuser/catty-reminders-app"

echo "Deploying via Docker Compose..."

ssh -p "$TARGET_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT
    set -e

    export REPO_LOWER="${REPO_LOWER}"
    export RELEASE_HASH="${RELEASE_HASH}"
    export MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}"
    export MYSQL_USER="${MYSQL_USER}"
    export MYSQL_PASSWORD="${MYSQL_PASSWORD}"

    echo "--> Navigating to application directory"
    cd ${APP_DIR}

    echo "--> Stopping old compose stack"
    docker compose down

    echo "--> Pulling latest images"
    docker compose pull

    echo "--> Starting containers"
    docker compose up -d

    echo "--> Cleaning up old unused images"
    docker image prune -af || true
    
    echo "--> Deployment finished successfully"
REMRE_SCRIPT
