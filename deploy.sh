#!/bin/bash

set -e

cd "/home/seva/Documents/catty-reminders-app"

echo "Pulling latest changes..."
git pull

echo "Updating deployref..."
git rev-parse HEAD > deployref.txt

echo "Restarting app..."

pkill -f "python3 app.py" || true

nohup ./venv/bin/python app.py > app.log 2>&1 &

echo "Deploy completed"
