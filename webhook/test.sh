#!/bin/bash
set -e

BRANCH=$1
APP_DIR="/home/mzpdqk/devops/catty-reminders-app"

echo "=== test: $BRANCH ==="

if [ -z "$BRANCH" ]; then
    echo "branch not provided"
    exit 1
fi

cd "$APP_DIR"

git fetch origin
git checkout -B $BRANCH origin/$BRANCH
git reset --hard origin/$BRANCH

if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    source venv/bin/activate
    pip install -r requirements.txt
fi

# запуск приложения в фоне
"$APP_DIR/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8181 &
APP_PID=$!

sleep 3

export PYTHONPATH="$APP_DIR:$PYTHONPATH"

echo "run tests..."
pytest tests --maxfail=1 --disable-warnings -q

RESULT=$?

kill $APP_PID

exit $RESULT
