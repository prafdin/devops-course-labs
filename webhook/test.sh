set -e

BRANCH=$1
APP_DIR="/home/ubuntu/devops/catty-reminders-app"
VENV="$APP_DIR/venv"

echo "=== Запуск тестов проекта ветки $BRANCH ==="

# Создаем .env файл с правильным SHA
cd "$APP_DIR"
DEPLOY_REF="$(git rev-parse HEAD)"
echo "Текущий SHA ветки $BRANCH: $DEPLOY_REF"
echo "DEPLOY_REF=$DEPLOY_REF" > "$APP_DIR/.env"

# Проверяем и создаем виртуальное окружение если нужно
if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        echo "=== создание виртуального окружения $BRANCH ==="
        python3 -m venv venv
    fi
    echo "=== активация виртуального окружения $BRANCH ==="
    source venv/bin/activate
    echo "=== установка зависимостей $BRANCH ==="
    pip install -r requirements.txt
fi

# Убиваем старые процессы
echo "=== Останавливаем старые процессы ==="
pkill -f "uvicorn app.main:app" || true
sleep 2

# Запускаем приложение
echo "=== запуск приложения $BRANCH для тестов ==="
source venv/bin/activate
nohup uvicorn app.main:app --host 127.0.0.1 --port 8181 > /tmp/uvicorn.log 2>&1 &
APP_PID=$!

echo "APP_PID: $APP_PID"

# Ждем запуска приложения с проверкой
echo "=== Ожидаем запуск приложения ==="
MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://127.0.0.1:8181/login > /dev/null 2>&1; then
        echo "✅ Приложение запущено"
        break
    fi
    sleep 1
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ Приложение не запустилось за $MAX_ATTEMPTS секунд"
    cat /tmp/uvicorn.log
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

# Запускаем тесты
echo "=== Выполняем тесты из папки tests ==="
export PYTHONPATH=/home/ubuntu/devops/catty-reminders-app:$PYTHONPATH
PLAYWRIGHT_BROWSERS_PATH=/home/ubuntu/.cache/ms-playwright pytest tests --maxfail=1 --disable-warnings -q -v
RESULT=$?

# Останавливаем приложение
echo "=== Останавливаем приложение ==="
kill $APP_PID 2>/dev/null || true
sleep 2

exit $RESULT
