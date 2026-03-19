#!/bin/bash

set -e

REPO_URL="https://github.com/mappy12/catty-reminders-app"
LOG_FILE="/home/mappy/Desktop/catty-reminders-app/webhook/deploy.log"
APP_DIR="/home/mappy/Desktop/catty-reminders-app"
BRANCH=$1

log() {
	echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "НАЧАЛО ДЕПЛОЯ"
log "Ветка: $BRANCH"

if [ ! -d "$APP_DIR/.git" ]; then
	log "Репозиторий не найден. Клонирование..."
	git clone --branch $BRANCH $REPO_URL $APP_DIR
else
	log "Репозиторий найден..."
fi

cd $APP_DIR

log "Получение последних изменений..."
git fetch origin
git checkout $BRANCH
git reset --hard origin/$BRANCH

if [ -f "requirements.txt" ]; then
	log "Установка зависимостей..."
	if [ ! -d "venv" ]; then
		log "Создание виртуального окружения..."
		python3 -m venv venv
	fi

	source venv/bin/activate
	pip install -r requirements.txt

	pip install pytest
else
	log "requirements.txt не найден"
fi

log "ЗАПУСК ТЕСТОВ"

export PYTHONPATH=$APP_DIR:$PYTHONPATH

if [ -d "tests" ]; then
	if pytest tests -v --maxfail=1 --disable-warnings; then
		TEST_RESULT=$?
		log "Тесты прошли успешно!"
	else
		TEST_RESULT=$?
		log "Тесты не прошли! Код ошибки: $TEST_REUSLT"
		log "Остановка деплоя."
		exit $TEST_RESULT
	fi
else
	log "Папки tests не существует, переходим к запуску приложения..."
fi

log "Выполняется перезапуск приложения..."
sudo systemctl restart app

log "ДЕПЛОЙ ДЛЯ ВЕТКИ $BRANCH ЗАВЕРШЕН УСПЕШНО"
log ""
