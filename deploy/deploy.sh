#!/bin/bash

set -e

REPO_DIR="/mnt/c/Users/Sergo/Documents/prog/university/catty-reminders-app"
BRANCH=$1

echo "Deploying $BRANCH branch"


cd "$REPO_DIR"
echo "Directory changed to $REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
echo "Pull $BRANCH branch"
git pull origin "$BRANCH"

DEPLOY_REF=$(git rev-parse HEAD | tr -d '\r')
echo "DEPLOY_REF=$DEPLOY_REF" > /mnt/c/Users/Sergo/Documents/prog/university/catty-reminders-app/.env.deploy
echo "Deploy ref: $DEPLOY_REF"

if [ ! -d ".venv" ]; then
	echo "Virtual environment was not found, creating..."
	python3 -m venv .venv/
fi

source .venv/bin/activate
echo "Virutal environment activated"

if [ -f "requirements.txt" ]; then
	echo "Installing/Updating requirements"
	pip install -r requirements.txt
fi

echo "Restarting app..."
sudo systemctl restart app.service
echo "Done"