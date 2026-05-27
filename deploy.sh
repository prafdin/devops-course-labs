#!/bin/bash
set -e

APP_DIR="/home/qzm/Desktop/catty-reminders-app"

ssh -p "$SERVER_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT
    set -e
    export REPO_LOWER="${REPO_LOWER}\"
    export RELEASE_HASH="${RELEASE_HASH}\"

    cd ${APP_DIR}
    
    echo \"Stopping old stack\"
    docker compose down || true
    
    echo \"Pulling images\"
    docker compose pull
    
    echo \"Starting new stack\"
    docker compose up -d
    
    docker image prune -af
REMOTE_SCRIPT
