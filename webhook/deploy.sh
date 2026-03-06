#!/bin/bash

set -e

REPO_DIR="/home/ct/catty-reminders-app"
BRANCH=$1

echo ">Deploying $BRANCH branch"


cd "$REPO_DIR"
echo ">Directory changed to $REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
echo ">Pull $BRANCH branch"
git pull origin "$BRANCH"

if [ ! -d ".venv" ]; then
	echo ">Virtual environment was not found, creating..."
	python3 -m venv .venv/
fi

source .venv/bin/activate
echo ">Virutal environment activated"

if [ -f "requirements.txt" ]; then
	echo ">Installing/Updating requirements"
	pip install -r requirements.txt
fi

echo ">Restarting app..."
sudo systemctl restart app
echo ">Done"
