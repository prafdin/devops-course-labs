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
log_message "INFO" "Начало развертывания ветки: $BRANCH"
log_message "INFO" "========================================="

cd "$PROJECT_DIR" || exit 1
check_success "Переход в директорию $PROJECT_DIR"

if [ ! -d "$PROJECT_DIR/.git" ]; then
    log_message "INFO" "Первый запуск - инициализация репозитория в существующей папке"
    git init
    git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
    git fetch origin
    git reset --hard "origin/$BRANCH"
    check_success "Инициализация и получение данных из репозитория"
else
    log_message "INFO" "Обновление существующего репозитория"
    git fetch --all --prune
    check_success "Fetch изменений"
fi

git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH" "origin/$BRANCH"
git reset --hard "origin/$BRANCH"
check_success "Переключение на ветку $BRANCH"

git pull origin "$BRANCH"
check_success "Pull последних изменений"

LAST_COMMIT=$(git rev-parse HEAD)
log_message "INFO" "Последний коммит: $LAST_COMMIT"

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
        log_message "INFO" "Создание виртуального окружения"
        python3 -m venv venv
        check_success "Создание venv"
    fi
    
    log_message "INFO" "Активация виртуального окружения"
    source venv/bin/activate
    check_success "Активация venv"
    
    log_message "INFO" "Обновление pip"
    pip install --upgrade pip > /dev/null 2>&1
    
    log_message "INFO" "Установка зависимостей"
    pip install -r requirements.txt
    check_success "Установка зависимостей"
fi

log_message "INFO" "Перезапуск systemd сервиса"
if systemctl --user is-active --quiet "$SERVICE_NAME"; then
    systemctl --user restart "$SERVICE_NAME"
    check_success "Перезапуск $SERVICE_NAME"
else
    log_message "WARNING" "Сервис $SERVICE_NAME не активен"
    log_message "INFO" "Запуск сервиса"
    systemctl --user start "$SERVICE_NAME"
    check_success "Запуск $SERVICE_NAME"
fi

sleep 2
if systemctl --user is-active --quiet "$SERVICE_NAME"; then
    log_message "SUCCESS" "Сервис успешно запущен на порту 8181"
else
    log_message "ERROR" "Не удалось запустить сервис"
    exit 1
fi

log_message "SUCCESS" "========================================="
log_message "SUCCESS" "Развертывание успешно завершено!"
log_message "SUCCESS" "Ветка: $BRANCH, Коммит: $LAST_COMMIT"
log_message "SUCCESS" "========================================="
