#!/bin/bash
cd /home/password_123/catty-reminders-app || exit 1
SHA=$1
echo "Deploying SHA: $SHA"
git fetch --all
git reset --hard "$SHA"
/home/password_123/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env
sudo systemctl restart catty
sleep 3
if systemctl is-active --quiet catty; then
    echo "SUCCESS: SHA: $SHA"
else
    echo "ERROR"
    exit 1
fi
