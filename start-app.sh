#!/bin/bash
cd /home/yaroslav/devops-lab/catty-reminders-app
export DEPLOY_REF=$(/usr/bin/git rev-parse HEAD)
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8181
