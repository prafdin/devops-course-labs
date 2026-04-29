#!/bin/bash
cd /home/vboxuser/devops/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

git fetch --all
git reset --hard "$SHA"

/home/vboxuser/devops/venv/bin/python -m pip install -r requirements.txt

echo "DEPLOY_REF=$SHA" | sudo tee /home/vboxuser/devops/catty-reminders-app/.env

sudo systemctl restart catty-app

sleep 3
if systemctl is-active --quiet catty-app; then
    echo "SUCCESS: Deployed $SHA"
else
    echo "ERROR: App failed"
    exit 1
fi
