#!/bin/bash

# Скрипт автоматического развертывания
# Завершаем скрипт при любой ошибке
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Starting deployment at $(date) ==="

# 1. Забираем последние изменения из репозитория
echo "1. Pulling latest code..."

git pull

# 2. Настройка виртуального окружения и обновление зависимостей
echo "2. Setting up dependencies..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Запуск тестов
echo "3. Running tests..."
python -m pytest tests/

# 4. Перезапуск веб-сервера
echo "4. Restarting main application service..."

if ! python -m pytest tests/; then
    echo "ERROR: Tests failed! Performing rollback to the previous version..."
    
    git reset --hard ORIG_HEAD
    
    exit 1
fi

echo "Tests passed successfully!"

echo "4. Updating DEPLOY_REF..."
echo "DEPLOY_REF=$(git rev-parse HEAD)" > .env

echo "5. Restarting main application service..."

sudo systemctl restart app.service

echo "=== Deployment finished successfully ==="
