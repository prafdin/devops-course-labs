#!/bin/bash

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="/home/Roman/Desktop/catty-reminders-app"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Установка webhook обработчика${NC}"
echo -e "${BLUE}========================================${NC}"

if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${BLUE}Создание .env файла...${NC}"
    cat > "$PROJECT_DIR/.env" << EOF
PROJECT_PATH=$PROJECT_DIR
REPO_URL=https://github.com/RenTogan/catty-reminders-app.git
WEBHOOK_PORT=8080
BRANCH=lab1

DEPLOY_COMMIT=
DEPLOY_BRANCH=
DEPLOY_TIME=
EOF
    echo -e "${GREEN}.env файл создан${NC}"
fi

chmod +x "$PROJECT_DIR/deploy_app.sh"
chmod +x "$PROJECT_DIR/run_tests.sh"
chmod +x "$PROJECT_DIR/webhook_handler.py"

echo -e "${GREEN}Скрипты готовы к запуску${NC}"

mkdir -p /home/Roman/.config/systemd/user

rm -f /home/Roman/.config/systemd/user/webhook-handler.service
rm -f /home/Roman/.config/systemd/user/catty-app.service

cat > /home/Roman/.config/systemd/user/webhook-handler.service << 'EOF'
[Unit]
Description=GitHub Webhook Handler for catty-reminders
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/Roman/Desktop/catty-reminders-app
ExecStart=/usr/bin/python3.13 /home/Roman/Desktop/catty-reminders-app/webhook_handler.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

echo -e "${GREEN}Создан systemd сервис webhook-handler${NC}"

cat > /home/Roman/.config/systemd/user/catty-app.service << 'EOF'
[Unit]
Description=Catty Reminders Web Application
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/Roman/Desktop/catty-reminders-app
ExecStart=/usr/bin/python3.13 -m uvicorn app.main:app --host 0.0.0.0 --port 8181
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

echo -e "${GREEN}Создан systemd сервис catty-app${NC}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Настройка FRP...${NC}"

PROXY="course.prafdin.ru"
TOKEN="devops"
ID="mansurov"

sudo tee /etc/frp/frpc.toml > /dev/null <<EOF
serverAddr = "$PROXY"
serverPort = 7000
auth.method = "token"
auth.token = "$TOKEN"

[[proxies]]
name = "hook-$ID"
type = "http"
localPort = 8080
customDomains = ["webhook.$ID.$PROXY"]

[[proxies]]
name = "app-$ID"
type = "http"
localPort = 8181
customDomains = ["app.$ID.$PROXY"]
EOF

sudo systemctl daemon-reload
sudo systemctl enable frpc
sudo systemctl restart frpc

echo -e "${GREEN}FRP настроен и запущен${NC}"

systemctl --user daemon-reload

systemctl --user stop webhook-handler.service catty-app.service 2>/dev/null || true

systemctl --user start webhook-handler.service
systemctl --user start catty-app.service

systemctl --user enable webhook-handler.service
systemctl --user enable catty-app.service

echo -e "${GREEN}Webhook сервис запущен${NC}"
echo -e "${GREEN}Основное приложение запущено${NC}"

sleep 2
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Статус сервисов:${NC}"
systemctl --user status webhook-handler.service --no-pager --lines=0
systemctl --user status catty-app.service --no-pager --lines=0
echo -e "${BLUE}FRP статус:${NC}"
sudo systemctl status frpc --no-pager --lines=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Проверка портов:${NC}"
ss -tlnp | grep -E "8080|8181" || echo -e "${RED}Порты не слушаются${NC}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Локальная проверка:${NC}"
curl -s http://localhost:8080/health || echo -e "${RED}Webhook не отвечает${NC}"
curl -s http://localhost:8181 || echo -e "${RED}Приложение не отвечает${NC}"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Установка завершена!${NC}"
echo -e "${BLUE}Webhook URL: http://webhook.mansurov.course.prafdin.ru/webhook${NC}"
echo -e "${BLUE}Приложение: http://app.mansurov.course.prafdin.ru${NC}"
echo -e "${BLUE}========================================${NC}"
