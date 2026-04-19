#!/bin/bash
set -e

IMAGE_NAME=$1
DEPLOY_REF=$2

# Пути и настройки
APP_DIR="/home/rover/catty-reminders-app"
COMPOSE_FILE="$APP_DIR/docker-compose.yaml"

echo "=== DEPLOY релиза: $DEPLOY_REF ==="

cd $APP_DIR

# 1. Создаем/обновляем .env файл прямо на сервере
# (чтобы подставить актуальный тег образа)
cat > .env << EOF
DB_CONTAINER_NAME=catty-db
MARIADB_ROOT_PASSWORD=mypass
MARIADB_USER=root
MARIADB_PASSWORD=mypass
MARIADB_DATABASE=catty_reminders
HOST_DB_PORT=3306
CONTEINER_DB_PORT=3306

APP_CONTAINER_NAME=catty-reminders-app
IMAGE=${IMAGE_NAME}:${DEPLOY_REF}
DEPLOY_REF=${DEPLOY_REF}
HOST_APP_PORT=8181
CONTEINER_APP_PORT=8181
EOF

echo "=== Скачиваю новый образ ==="
docker pull "${IMAGE_NAME}:${DEPLOY_REF}"

echo "=== Перезапускаю стек через Docker Compose ==="
# down не удалит volume с данными (db_data), так что данные БД сохранятся!
docker compose down
docker compose up -d

echo "=== Жду запуска приложения ==="
for i in {1..30}; do
    if curl -sf http://localhost:8181/login | grep -q "Catty"; then
        echo "Приложение успешно запустилось!"
        docker compose ps
        exit 0
    fi
    sleep 2
done

echo "Ошибка: Приложение не ответило в течение 60 секунд."
docker compose logs --tail=50
exit 1
