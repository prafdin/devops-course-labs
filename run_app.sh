#!/bin/bash
# Заходим в папку проекта
cd /home/ilya/catty-reminders-app || exit 1

SHA=$1

# 1. Принудительно обновляем код
git fetch origin lab2
git reset --hard "$SHA"

# 2. Обновляем зависимости в venv
./venv/bin/pip install -r requirements.txt

# 3. Записываем хэш в файл окружения (чтобы сайт показал его боту)
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env

# 4. Перезапускаем сервис через systemd
sudo systemctl restart catty

# 5. Проверка
sleep 3
if systemctl is-active --quiet catty; then
    echo "SUCCESS: Catty service restarted with SHA $SHA"
else
    echo "ERROR: Catty service failed to start"
    sudo journalctl -u catty -n 20
    exit 1
fi
