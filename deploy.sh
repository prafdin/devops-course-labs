#!/bin/bash
SERVICE="catty"
DEPLOY_REF=$1
APP_DIR="/home/vboxuser/catty-reminders-app"
cd $APP_DIR || exit 1
git fetch --all
git reset --hard $DEPLOY_REF
echo "DEPLOY_REF=$DEPLOY_REF" | sudo tee /etc/catty-app-env
sudo systemctl restart $SERVICE
sleep 2
if systemctl is-active --quiet $SERVICE; then
    echo "DEPLOY SUCCESS"
else
    echo "DEPLOY FAILED"
    exit 1
fi
