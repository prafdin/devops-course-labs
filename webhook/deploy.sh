#!/bin/bash

set -e

REPO_URL="https://github.com/mappy12/catty-reminders-app"
LOG_FILE="/home/mappy/webhook/deploy.log"
APP_DIR="/home/mappy/Desktop/catty-reminders-app"
ENV_FILE="$APP_DIR/.env"

BRANCH=$1

log() {
	echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "НАЧАЛО ДЕПЛОЯ"
log "Ветка: $BRANCH"

TMP_DIR=$(mktemp -d)
log "Временная директория: $TMP_DIR"

log "Клонирование репозитория..."
git clone --branch $BRANCH $REPO_URL $TMP_DIR

cp -r $APP_DIR/testlib $TMP_DIR/tests/

export PYTHONPATH=$TMP_DIR:$PYTHONPATH

cd $TMP_DIR

log "Установка зависимостей во временной папке..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

if pytest tests -v --maxfail=1 --disable-warnings; then
    TEST_RESULT=$?
    log "ТЕСТЫ ПРОШЛИ УСПЕШНО!"
    
    DEPLOY_REF=$(git rev-parse HEAD)
    log "SHA коммита: $DEPLOY_REF"
    
    log "Настройка переменной окружения для приложения..."
    
    echo "DEPLOY_REF=$DEPLOY_REF" > $ENV_FILE  
    
    log "Обновление рабочей папки приложения..."
    
    rsync -a --delete \
        --exclude='venv' \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        $TMP_DIR/ $APP_DIR/
    
    log "Перезапуск приложения..."
    sudo systemctl restart app
    
    log "=== ДЕПЛОЙ ДЛЯ ВЕТКИ $BRANCH УСПЕШНО ЗАВЕРШЕН ==="

else
    TEST_RESULT=$?
    log "ТЕСТЫ НЕ ПРОШЛИ! Код ошибки: $TEST_RESULT"
    log "Остановка деплоя."
    
    exit $TEST_RESULT

fi

log "Очистка временной директории..."
rm -rf $TMP_DIR
