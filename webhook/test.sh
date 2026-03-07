#!/bin/bash

set -e

REPO_DIR="/home/ct/catty-reminders-app/"
BRANCH=$1

cd "$REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
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

#echo "> Starting temporary app"
#uvicorn app.main:app --host 127.0.0.1 --port 8181 > /tmp/catty-test.log 2>&1 &
#APP_PID=$!

#sleep 4

echo "> Running pytest"
python3 -m pytest -v

#RESULT=$?

#echo "> Stopping temporary app"
#kill "$APP_PID"

#exit "$RESULT"
echo ">Tests finished"
