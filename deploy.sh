#!/bin/bash
set -e

cd /home/vboxuser/catty-reminders-app

git fetch origin
git checkout lab1
git pull origin lab1

git rev-parse HEAD > deployref.txt

if [ -f requirements.txt ]; then
    python3 -m pip install --break-system-packages -r requirements.txt
fi

if [ -d tests ]; then
    python3 -m unittest discover tests
fi

sudo systemctl restart catty.service
