#!/bin/zsh
set -e

TARGET_DIR="/home/light/catty-reminders-app"

BRANCH=${1:-lab1}
COMMIT_SHA=$2

echo "Переходим в директорию $TARGET_DIR..."
cd "$TARGET_DIR"

echo "Стягиваем последние изменения..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"

echo "Записываем хэш коммита в .env..."
if [ -z "$COMMIT_SHA" ] || [ "$COMMIT_SHA" == "unknown" ]; then
    COMMIT_SHA=$(git rev-parse HEAD)
fi
echo "DEPLOY_REF=$COMMIT_SHA" > "$TARGET_DIR/.env"

echo "Обновляем зависимости..."
source .venv/bin/activate
pip install -r requirements.txt

echo "Перезапускаем системную службу uvicorn..."
sudo systemctl restart catty-app

sleep 5

echo "Запускаем тесты..."
./test.sh

echo "Развертывание завершено успешно!"
