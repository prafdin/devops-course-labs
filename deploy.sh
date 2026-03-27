#!/bin/bash

set -e

REPO_DIR="/home/yui1337/my_project"
BRANCH=$1

echo ">Deploying $BRANCH branch"

cd "$REPO_DIR"
echo ">Directory changed to $REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
echo ">Pull $BRANCH branch"
git pull origin "$BRANCH"

DEPLOY_REF=$(git rev-parse HEAD)
echo "DEPLOY_REF=$DEPLOY_REF" > "$REPO_DIR/.env"
echo ">Deploy ref: $DEPLOY_REF"

if [ ! -d "venv" ]; then
    echo ">Virtual environment was not found, creating..."
    python3 -m venv venv
fi

source venv/bin/activate
echo ">Virtual environment activated"

if [ -f "requirements.txt" ]; then
    echo ">Installing/Updating requirements"
    pip install -r requirements.txt
fi

echo ">Running tests..."
pip install pytest 

# Если тесты упадут, скрипт прервется здесь из-за 'set -e'
python3 -m pytest
echo ">Tests passed successfully!"

echo ">Restarting app..."
sudo systemctl restart catty.service
echo ">Done"
