#!/bin/bash

set -e

cd /home/vboxuser/catty-reminders-app

BRANCH="$1"
COMMIT_HASH=$(git rev-parse "origin/$BRANCH")

if [ -z "$COMMIT_HASH" ]; then
    echo "ERROR: Commit hash is not provided!"
    exit 1
fi

git fetch origin
git checkout "$COMMIT_HASH"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python3 -m playwright install chromium

if ! python3 -m pytest tests/; then
    echo "ERROR: Tests failed! Performing rollback to the previous version..."
    git checkout -
    echo "Restarting main application service to apply rollback..."
    sudo systemctl restart catty
    exit 1
fi

echo "DEPLOY_REF=$COMMIT_HASH" > .env

sudo systemctl restart catty

