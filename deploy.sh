#!/bin/bash

set -e

cd cd "/home/seva/Documents/catty-reminders-app"


echo "Pulling latest changes..."
git pull

echo "Updating deployref..."
git rev-parse HEAD > deployref.txt

echo "Restarting app..."

pkill -f "python3 app.py" || true

nohup python3 app.py > app.log 2>&1 &

echo "Deploy completed"