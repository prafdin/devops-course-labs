#!/bin/bash
# Go to the project folder
cd /home/ubu/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

# Update the code from GitHub
git fetch --all
git reset --hard "$SHA"

# Update dependencies
/home/ubu/catty-reminders-app/venv/bin/python -m pip install -r requirements.txt

# Save DEPLOY_REF for display on the website
echo "DEPLOY_REF=$SHA" | sudo tee /etc/catty-app-env

# Restart the application itself
sudo systemctl restart catty

# Check
sleep 3
if systemctl is-active --quiet catty; then
echo "SUCCESS: Deployed $SHA"
else
echo "ERROR: App failed"
exit 1
fi
