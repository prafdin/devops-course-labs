#!/bin/bash
# Настройка переменных. Актуальные значения узнайте у преподавателя
PROXY=course.prafdin.ru
TOKEN=devops
ID=shtengauer
# Скачать и установить frp как systemd сервисы.
# Команда запросит пароль текущего пользователя
wget -qO- https://gist.github.com/lawrenceching/\
41244a182307940cc15b45e3c4997346/raw/\
0576ea85d898c965c3137f7c38f9815e1233e0d1/\
install-frp-as-systemd-service.sh | sudo bash
# Настройка доступа до frp server.
# Команда запросит пароль текущего пользователя
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
# Конец команды
# Запустите frp client. Команда запросит пароль текущего пользователя
sudo systemctl start frpc
# Проверьте корректность настройки
echo "Адрес для проверки: webhook.$ID.$PROXY"
wget -qO- https://gist.githubusercontent.com/\
prafdin/b9ff40c8bc6dc8c55ca7ac911e278ecc\
/raw/8134f5f34220576bfc8cd205910e1625d66b58cb\
/main.py | python3
# Перейдите по адресу для проверки в браузере.
# Если всё настроено правильно, то в браузере получите ok
