#!/bin/bash
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
cd "$REPO_DIR"

source .venv/bin/activate

export python_test_url="http://127.0.0.1:8181"
export BASE_URL="http://127.0.0.1:8181"

uvicorn main:app --host 127.0.0.1 --port 8181 > /tmp/test_app.log 2>&1 &
APP_PID=$!

sleep 5
python3 -m pytest -v --base-url http://127.0.0.1:8181
