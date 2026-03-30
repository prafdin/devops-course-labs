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


set -a
source .env.deploy
set +a

echo "=== запуск pytest ==="

export PYTHONPATH=$PWD

pytest tests \
  --maxfail=1 \
  --disable-warnings \
  -q

RESULT=$?

exit $RESULT
