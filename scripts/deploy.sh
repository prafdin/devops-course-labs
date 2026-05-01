#!/bin/bash

set -e

if [[ -z "$SERVER_HOST" || -z "$SERVER_USER" ]]; then
    echo "CRITICAL: SERVER_HOST and SERVER_USER variables are required."
    exit 1
fi

if [[ -z "$RELEASE_HASH" ]]; then
    echo "CRITICAL: RELEASE_HASH is missing."
    exit 1
fi

# Если порт не передан, ставим 22 по умолчанию
TARGET_PORT="${SERVER_PORT:-22}"
APP_DIR="/home/killa123/Desktop/devopss/catty-reminders-app"

echo "=== Starting deployment process ==="
echo "Target: ${SERVER_USER}@${SERVER_HOST}:${TARGET_PORT}"
echo "Updating to commit: ${RELEASE_HASH}"

ssh -p "$TARGET_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "bash -s" << REMOTE_SCRIPT
    set -e

    echo "--> Navigating to application directory"
    cd ${APP_DIR}
    
    echo "--> Fetching latest changes"
    git fetch origin
    
    echo "--> Checking out specific release commit"
    git checkout ${RELEASE_HASH}
    
    CURRENT_REF=\$(git rev-parse HEAD)
    echo "DEPLOY_REF=\$CURRENT_REF" > .env
    echo "--> Successfully written DEPLOY_REF: \$CURRENT_REF"
    
    echo "--> Setting up Virtual Environment"
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    echo "--> Installing dependencies"
    if [[ -f "requirements.txt" ]]; then
        python -m pip install -r requirements.txt
    fi
    
    echo "--> Restarting Systemd Service"
    sudo systemctl restart app.service
    
    echo "--> Verifying application status..."
    sleep 5
    
    if sudo systemctl is-active --quiet app.service; then
        echo "=== Deployment successful ==="
    else
        echo "=== DEPLOYMENT FAILED: Service is not active ==="
        exit 1
    fi
REMOTE_SCRIPT