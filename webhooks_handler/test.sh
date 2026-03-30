#!/bin/bash
set -e

echo "=== Запуск тестов ==="

cd "$(dirname "$0")/.."

DEPLOY_REF="$(git rev-parse HEAD)"
echo "DEPLOY_REF=$DEPLOY_REF" > .env.deploy

echo "Текущий SHA: $DEPLOY_REF"

if [ ! -d "venv" ]; then
    echo "=== создание venv ==="
    python -m venv venv
fi

source venv/bin/activate

echo "=== установка зависимостей ==="
pip install -r requirements.txt
pip install playwright
playwright install --with-deps

set -a
source .env.deploy
set +a

uvicorn app.main:app --host 127.0.0.1 --port 8181 &
sleep 3

echo "=== запуск pytest ==="

export PYTHONPATH=$PWD

pytest tests \
  --maxfail=1 \
  --disable-warnings \
  -q

RESULT=$?
lsof -ti:8181 | xargs kill -9 || true
exit $RESULT
