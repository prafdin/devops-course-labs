#!/bin/bash
cd /home/enjoyer/my-app
git fetch origin lab1
git reset --hard origin/lab1
./venv/bin/pip install -r requirements.txt
sudo systemctl restart catty-app
