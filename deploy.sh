#!/bin/bash
set -e

DEPLOY_REF=$1
REPO_URL="git@github.com:Rovver52/catty-reminders-app"
APP_DIR="/home/${USER}/catty-reminders-app"

echo "=== 🚀 DEPLOY релиза ==="
echo "Commit SHA: $DEPLOY_REF"
echo "APP_DIR: $APP_DIR"

if [ ! -d "$APP_DIR/.git" ]; then
    echo "📦 Первый запуск — клонирование репозитория"
    mkdir -p "$APP_DIR"
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

echo "🔄 Подтягиваем обновления..."
git fetch --all --tags

echo "🔖 Переходим на коммит: $DEPLOY_REF"
git c…здаём виртуальное окружение..."
        python3 -m venv venv
    fi
    echo "✅ Активируем venv и устанавливаем зависимости..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo "🔁 Перезапускаем сервис myapp..."
sudo systemctl restart catty

sleep 3
if sudo systemctl is-active --quiet catty; then
    echo "✅ Деплой завершён успешно!"
else
    echo "❌ Ошибка: сервис myapp не запустился"
    sudo systemctl status catty --no-pager
    exit 1
fi
