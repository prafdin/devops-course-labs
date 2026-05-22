#!/bin/bash

set -Eeuo pipefail

(
flock -n 9 || {
    echo "[DEPLOY] Deployment already running"
    exit 1
}

LOG_FILE="$HOME/catty-reminders-app/deploy.log"

exec >> "$LOG_FILE" 2>&1

echo "========================================"
echo "[DEPLOY] $(date)"

BRANCH="${1:-lab1}"

PROJECT_DIR="$HOME/catty-reminders-app"

echo "[DEPLOY] Project dir: $PROJECT_DIR"
echo "[DEPLOY] Branch: $BRANCH"

cd "$PROJECT_DIR"

echo "[DEPLOY] Fetching changes"

git fetch origin

# Проверяем существование ветки
if ! git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
    echo "[DEPLOY] Branch '$BRANCH' does not exist"
    exit 1
fi

echo "[DEPLOY] Checkout branch"

git checkout "$BRANCH"

echo "[DEPLOY] Resetting repository state"

git reset --hard "origin/$BRANCH"

echo "[DEPLOY] Cleaning repository"

git clean -fd

# Создание .env
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "[DEPLOY] Creating .env"

    cp .env.example .env
fi

# Создание virtualenv
if [ ! -d "venv" ]; then
    echo "[DEPLOY] Creating virtualenv"

    python3 -m venv venv
fi

echo "[DEPLOY] Activating virtualenv"

source venv/bin/activate

echo "[DEPLOY] Upgrading pip"

pip install --upgrade pip

echo "[DEPLOY] Installing dependencies"

pip install -r requirements.txt

# Проверка Python syntax
echo "[DEPLOY] Running syntax checks"

find . -type f -name "*.py" \
    -not -path "./venv/*" \
    -exec python3 -m py_compile {} \;

# Установка playwright browser
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo "[DEPLOY] Installing Playwright Chromium"

    playwright install --with-deps chromium
fi

echo "[DEPLOY] Restarting application"

sudo systemctl restart catty

echo "[DEPLOY] Waiting for startup"

sleep 5

echo "[DEPLOY] Running healthcheck"

if ! curl -fsS http://127.0.0.1:8181 >/dev/null; then
    echo "[DEPLOY] Healthcheck failed"

    sudo systemctl status catty --no-pager

    exit 1
fi

# Тесты
if [ -d tests ]; then
    echo "[DEPLOY] Running tests"

    python3 -m pytest -v
fi

echo "[DEPLOY] Deployment completed successfully"

) 9>/tmp/catty-deploy.lock
