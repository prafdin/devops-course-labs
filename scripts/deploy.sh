#!/bin/bash

set -e

if [ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ]; then
    echo "Error: DEPLOY_HOST and DEPLOY_USER must be set"
    exit 1
fi

if [ -z "$BRANCH" ]; then
    echo "Error: BRANCH must be set"
    exit 1
fi

DEPLOY_PORT=${DEPLOY_PORT:-22}
DEPLOY_DIR="/home/ct/catty-reminders-app"

echo "Deploying to $DEPLOY_HOST:$DEPLOY_PORT"
echo "User: $DEPLOY_USER"
echo "Branch: $BRANCH"

SSH_OPTIONS="-p $DEPLOY_PORT -o StrictHostKeyChecking=no"

ssh $SSH_OPTIONS "$DEPLOY_USER@$DEPLOY_HOST" << EOF
    set -e
    
    cd $DEPLOY_DIR
    
    git fetch origin
    git checkout -B $BRANCH origin/$BRANCH
    git pull origin $BRANCH
    
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
    
    echo "Deployment completed successfully"
EOF