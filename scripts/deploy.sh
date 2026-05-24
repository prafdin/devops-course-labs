#!/bin/bash

set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" || -z "$REPO_NAME" ]]; then
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"

REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')
IMAGE_NAME="ghcr.io/${REPO_LOWER}:${RELEASE_HASH}"

ssh -p "$TARGET_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT
    set -e

    sudo systemctl stop app.service || true
    sudo systemctl disable app.service || true

    docker pull \${IMAGE_NAME}

    docker stop catty-app || true
    docker rm catty-app || true

    docker run -d \
      --name catty-app \
      --restart always \
      -p 8181:8181 \
      --env-file /home/yarik/Desktop/catty-reminders-app/.env \
      \${IMAGE_NAME}

    sleep 5

    if [ \$(docker inspect -f '{{.State.Running}}' catty-app) == "true" ]; then
        exit 0
    else
        docker logs catty-app
        exit 1
    fi
REMOTE_SCRIPT
