#!/bin/bash
cd /home/vboxuser/lab2/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

git fetch --all
git reset --hard "$SHA"

/home/vboxuser/lab2/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt

# Принудительно убиваем все процессы на порту 8181
sudo fuser -k 8181/tcp 2>/dev/null
sudo pkill -9 -f uvicorn 2>/dev/null

sleep 2

echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env
sudo systemctl restart catty-app

sleep 5
if systemctl is-active --quiet catty-app; then
    echo "SUCCESS: Deployed $SHA"
else
    echo "ERROR: App failed"
    sudo journalctl -u catty-app -n 10 --no-pager
    exit 1
fi
