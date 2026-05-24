#!/bin/bash
set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" || -z "$RELEASE_HASH" || -z "$REPO_NAME" ]]; then
    exit 1
fi

REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

ssh -p "${SERVER_PORT:-22}" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" << REMOTE_SCRIPT
    cd /home/qzm/catty-compose
    
    echo "REPO_LOWER=${REPO_LOWER}" > .env
    echo "RELEASE_HASH=${RELEASE_HASH}" >> .env
    
    docker compose pull
    docker compose up -d --remove-orphans --force-recreate
    
    docker image prune -af
REMOTE_SCRIPT
