#!/bin/bash
cd ~/catty-reminders-app

# 1. Принудительно очищаем локальную ветку и тянем свежак
git fetch origin lab2
git reset --hard origin/lab2

# 2. Убиваем ВСЁ, что связано с приложением (-9)
pkill -9 -f "app.main" || true
pkill -9 -f "uvicorn" || true
pkill -9 -f "python3 -m app.main" || true

# 3. Даем системе секунду прийти в себя и проверяем, свободен ли порт 8181
sleep 1

# 4. Запускаем приложение
nohup python3 -m app.main --port 8181 </dev/null > deploy.log 2>&1 &

# 5. Финальная проверка для лога
sleep 3
ps aux | grep "app.main" | grep -v grep
echo "Deployment finished. Site should be updated now."
exit 0
