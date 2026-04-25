#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

BRANCH="${1:-lab1}"
PROJECT_DIR="${PROJECT_PATH:-/home/Roman/Desktop/catty-reminders-app}"
REPO_URL="${REPO_URL:-https://github.com/RenTogan/catty-reminders-app.git}"
SERVICE_NAME="catty-app"
LOG_FILE="$PROJECT_DIR/deploy.log"

log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

check_success() {
    if [ $? -eq 0 ]; then
        log_message "SUCCESS" "✓ $1"
    else
        log_message "ERROR" "✗ $1"
        exit 1
    fi
}

log_message "INFO" "========================================="
log_message "INFO" "Начало развертывания цели: $BRANCH"
log_message "INFO" "========================================="

cd "$PROJECT_DIR" || exit 1
check_success "Переход в директорию $PROJECT_DIR"

if [ ! -d "$PROJECT_DIR/.git" ]; then
    log_message "INFO" "Инициализация нового репозитория"
    git clone "$REPO_URL" .
    check_success "Клонирование репозитория"
else
    log_message "INFO" "Обновление индексов и тегов..."
    git fetch --all --tags --prune
    check_success "Fetch изменений и тегов"
fi

if git rev-parse --verify "origin/$BRANCH" >/dev/null 2>&1; then
    log_message "INFO" "Цель '$BRANCH' распознана как ветка. Обновляемся из origin."
    git checkout -B "$BRANCH" "origin/$BRANCH"
    git reset --hard "origin/$BRANCH"
elif git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    log_message "INFO" "Цель '$BRANCH' распознана как тег или хэш. Переключаемся."
    git checkout "$BRANCH"
    git reset --hard "$BRANCH"
else
    log_message "ERROR" "Ошибка: '$BRANCH' не найден в репозитории."
    exit 1
fi
check_success "Переключение на $BRANCH"

LAST_COMMIT=$(git rev-parse HEAD)
log_message "INFO" "Текущий коммит: $LAST_COMMIT"

if [ -f ".env" ]; then
    sed -i "/DEPLOY_COMMIT/d" .env 2>/dev/null || true
    sed -i "/DEPLOY_BRANCH/d" .env 2>/dev/null || true
    sed -i "/DEPLOY_TIME/d" .env 2>/dev/null || true
fi

echo "DEPLOY_COMMIT=$LAST_COMMIT" >> "$PROJECT_DIR/.env"
echo "DEPLOY_BRANCH=$BRANCH" >> "$PROJECT_DIR/.env"
echo "DEPLOY_TIME=$(date -Iseconds)" >> "$PROJECT_DIR/.env"

if [ -f "requirements.txt" ]; then
    log_message "INFO" "Настройка Python окружения"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        check_success "Создание venv"
    fi
    
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    check_success "Установка зависимостей"
fi

log_message "INFO" "Перезапуск systemd сервиса"
systemctl --user daemon-reload
if systemctl --user is-active --quiet "$SERVICE_NAME"; then
    systemctl --user restart "$SERVICE_NAME"
    check_success "Перезапуск $SERVICE_NAME"
else
    systemctl --user start "$SERVICE_NAME"
    check_success "Запуск $SERVICE_NAME"
fi

sleep 3
if systemctl --user is-active --quiet "$SERVICE_NAME"; then
    log_message "SUCCESS" "========================================="
    log_message "SUCCESS" "Развертывание завершено успешно!"
    log_message "SUCCESS" "Цель: $BRANCH, Коммит: $LAST_COMMIT"
    log_message "SUCCESS" "========================================="
else
    log_message "ERROR" "Сервис не смог запуститься после деплоя"
    exit 1
fi
