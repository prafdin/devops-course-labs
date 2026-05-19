#!/bin/bash
set -e

REF="$1"
COMMIT_SHA="$2"

cd /home/vboxuser/catty-reminders-app

git fetch origin

if [ -n "$REF" ]; then
    BRANCH="${REF#refs/heads/}"
    git checkout "$BRANCH"
    git reset --hard "$COMMIT_SHA"
else
    git checkout lab1
    git pull origin lab1
fi

git rev-parse HEAD > deployref.txt

if [ -f requirements.txt ]; then
    python3 -m pip install --break-system-packages -r requirements.txt
fi

if [ -d tests ]; then
    python3 -m unittest discover tests
fi

sudo systemctl restart catty.service
