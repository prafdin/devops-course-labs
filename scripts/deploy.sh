#!/bin/bash

set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" || -z "$REPO_NAME" ]]; then
    exit 1
fi

TARGET_PORT="${SERVER_PORT:-22}"
REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

ssh -p "$TARGET_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT
    set -e
    
    cd /home/yarik/Desktop/catty-reminders-app/

    export REPO_LOWER="${REPO_LOWER}"
    export RELEASE_HASH="${RELEASE_HASH}"
    
    docker compose pull
    docker compose up -d --remove-orphans

    sleep 5

    if [ \$(docker inspect -f '{{.State.Running}}' catty_backend) == "true" ]; then
        exit 0
    else
        docker logs catty_backend
        exit 1
    fi
REMOTE_SCRIPT
