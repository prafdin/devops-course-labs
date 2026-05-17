#!/bin/bash
cd /home/vboxuser/catty-reminders-app || exit 1
SHA=$1
echo "Deploying SHA: $SHA"
git fetch --all
git reset --hard "$SHA"
/home/vboxuser/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-env
sudo systemctl restart catty
sleep 3
if systemctl is-active --quiet catty; then
    echo "SUCCESS: SHA $SHA is live"
else
    echo "ERROR: catty service failed"
    exit 1
fi
