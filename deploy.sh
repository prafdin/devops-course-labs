#!/bin/bash
cd /home/vano/catty-app
COMMIT_SHA=$1
if [ -z "$COMMIT_SHA" ]; then
  COMMIT_SHA=$(git rev-parse HEAD)
fi
git fetch --all
git reset --hard "$COMMIT_SHA"
echo "DEPLOY_REF=$COMMIT_SHA" | sudo tee /tmp/deploy_ref.txt
sudo systemctl restart catty
echo "✅ Deployed $COMMIT_SHA"
