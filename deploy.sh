#!/bin/bash
echo "🚀 Начинаем развертывание catty-reminders-app..."

BRANCH=$1

# Путь к проекту (измените на свой)
APP_DIR="/home/victor/Desktop/DevOps/Lab_1/catty-reminders-app"


# 1. Обновляем код
echo "📦 Обновляем код из репозитория..."
cd $APP_DIR
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

# 2. Если есть зависимости, обновляем их (убедитесь, что pip3 установлен)
if [ -f "requirements.txt" ]; then
    source venv/bin/activate
    echo "📦 Обновляем зависимости..."
    pip3 install -r requirements.txt
fi

# 3. Перезапускаем приложение через systemd
COMMIT_HASH=$(git rev-parse HEAD)
echo "Код коммита: $COMMIT_HASH"
echo "DEPLOY_REF=$COMMIT_HASH" > .env
sudo /usr/bin/systemctl restart catty-app

echo "✅ Развертывание завершено!"
