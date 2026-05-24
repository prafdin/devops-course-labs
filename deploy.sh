#!/bin/bash
set -e

APP_DIR="/home/qzm/catty-compose"

echo "Deploying..."

ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" << REMOTE_SCRIPT
    cd ${APP_DIR}
    docker compose down --remove-orphans
    docker compose pull
    docker compose up -d
    docker image prune -af
REMOTE_SCRIPT
