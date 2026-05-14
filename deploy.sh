#!/bin/bash
cd /home/enjoyer/my-app
git pull origin lab1
CURRENT_SHA=$(git rev-parse HEAD)
echo "DEPLOY_REF=$CURRENT_SHA" > /home/enjoyer/my-app/.env
echo "DEPLOYREF=$CURRENT_SHA" >> /home/enjoyer/my-app/.env
./venv/bin/pip install -r requirements.txt
sudo systemctl restart catty-app
