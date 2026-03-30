#!/bin/bash

set -e

if [ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ]; then
    echo "Error: DEPLOY_HOST and DEPLOY_USER must be set"
    exit 1
fi

if [ -z "$RELEASE_HASH" ]; then
    echo "Error: RELEASE_HASH must be set"
    exit 1
fi

DEPLOY_PORT=${DEPLOY_PORT:-22}
DEPLOY_DIR="/home/ct/catty-reminders-app"

echo "Deploying to $DEPLOY_HOST:$DEPLOY_PORT"
echo "User: $DEPLOY_USER"
echo "Release hash: $RELEASE_HASH"
echo "Release branch: $RELEASE_BRANCH"

SSH_OPTIONS="-p $DEPLOY_PORT -o StrictHostKeyChecking=no"

ssh $SSH_OPTIONS "$DEPLOY_USER@$DEPLOY_HOST" << EOF
    set -e
    
    cd $DEPLOY_DIR
    
    git fetch origin
    git checkout $RELEASE_HASH
    
    DEPLOY_REF=\$(git rev-parse HEAD)
    echo "DEPLOY_REF=\$DEPLOY_REF" > .env.deploy
    echo "Deployed version: \$DEPLOY_REF"
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv/
    fi
    
    source .venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    sudo systemctl restart app.service
    
    sleep 4
    
    if sudo systemctl is-active --quiet app.service; then
        echo "Deployment completed successfully"
    else
        echo "ERROR: Application failed to start"
        exit 1
    fi
EOF