#!/bin/bash
echo "Deploying application..."
cd /home/ct/catty-reminders-app
git pull origin $1
sudo systemctl restart app.service
echo "Deployment completed!"
