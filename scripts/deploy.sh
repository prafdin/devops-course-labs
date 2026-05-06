#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" ]]; then
    echo "CRITICAL: Missing required variables."
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

APP_DIR="/home/killa123/Desktop/devopss/catty-reminders-app"

echo "Deploying via Docker Compose..."

ssh -p "$TARGET_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT
    set -e

    export REPO_LOWER="${REPO_LOWER}"
    export RELEASE_HASH="${RELEASE_HASH}"

    echo "--> Navigating to application directory"
    cd ${APP_DIR}

    echo "--> Stopping old containers"
    docker compose down

    echo "--> Pulling latest images"
    docker compose pull

    echo "--> Starting new containers"
    docker compose up -d

    echo "--> Cleaning up old unused images"
    docker image prune -af || true

    echo "--> Deployment finished successfully"
REMOTE_SCRIPT
