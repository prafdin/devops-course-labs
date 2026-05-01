#!/bin/bash
echo "Deploying $1"
echo "DEPLOY_REF=$1" | sudo tee /etc/catty-app-env
sudo systemctl daemon-reload
sudo systemctl restart catty
echo "Deployed ref: $(cat /etc/catty-app-env)"
