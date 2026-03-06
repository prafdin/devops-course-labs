#!/bin/bash

set -e

REPO_DIR="/home/ct/catty-reminders-app/"
BRANCH=$1

cd "$REPO_DIR"

git fetch origin
git checkout -B "$BRANCH"
echo ">Pull origin $BRANCH"
git pull origin "$BRANCH"

echo ">Running tests"

if [ ! -d ".venv" ]; then
	echo ">Virual environment was not found, creating..."
	python3 -m venv .venv/
fi

source .venv/bin/activate
echo ">Virtual environment activated"

if [ -f "requirements.txt" ]; then
	echo ">Installing/Updating requirements"
	pip install -r requirements.txt
fi


uvicorn app.main:app --reload --host 0.0.0.0 --port 8181
sleep 4
python3 -m pytest -v

echo ">Tests passed"
