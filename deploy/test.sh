#!/bin/bash
set -e
REPO_DIR="/mnt/c/Users/Sergo/Documents/prog/university/catty-reminders-app"
BRANCH=$1

cd "$REPO_DIR"
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git reset --hard "origin/$BRANCH"

source .venv/bin/activate

nohup uvicorn app.main:app --host 127.0.0.1 --port 8181 > /dev/null 2>&1 &
APP_PID=$!

sleep 3 

pytest tests -q
RESULT=$?

kill $APP_PID || true
exit $RESULT