#!/bin/bash
cd /home/kali/catty-reminders-app || exit 1
SHA=$1
git fetch --all
git reset --hard "$SHA"
/home/kali/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env
sudo systemctl restart catty
