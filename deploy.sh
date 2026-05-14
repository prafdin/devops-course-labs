#!/bin/bash
cd /home/enjoyer/my-app
git pull origin lab1
./venv/bin/pip install -r requirements.txt
sudo systemctl restart catty-app
echo "Deploy finished at $(date)"
