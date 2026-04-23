#!/bin/bash
echo "Deploying application..."
cd /home/ubuntu/devops-lab/app
pkill -f "python3.*app_server.py" 2>/dev/null
nohup python3 app_server.py 8181 > /dev/null 2>&1 &
echo "Deployment complete!"
