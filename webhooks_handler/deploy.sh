#!/bin/bash
set -e

BRANCH=$1
REPO_URL="git@github.com:APMorozov/catty-reminders-app"
APP_DIR="/home/alex/3kurs/dev-ops/catty-reminders-app"


echo "=== DEPLOY ветки $BRANCH ==="

if [ ! -d "$APP_DIR/.git" ]; then
    echo "Первый запуск — клонирование"
    git clone $REPO_URL $APP_DIR
fi

cd $APP_DIR

git fetch origin

git checkout -B $BRANCH origin/$BRANCH

git reset --hard origin/$BRANCH

if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        python -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
fi

uvicorn app.main:app --reload --host 0.0.0.0 --port 8181
