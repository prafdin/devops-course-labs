#!/bin/bash
set -x
set -e

CONTAINER_NAME="catty-app"
REGISTRY_IMAGE="ghcr.io/kuzminstanislav/catty-reminders-app"
TARGET_COMMIT=$1
PORT=8181

echo "> Deploying containerized app for commit: $TARGET_COMMIT"

sudo docker stop $CONTAINER_NAME || true
sudo docker rm $CONTAINER_NAME || true
sudo docker pull ${REGISTRY_IMAGE}:sha-${TARGET_COMMIT}

sudo docker run -d \
  --name $CONTAINER_NAME \
  --restart always \
  -p ${PORT}:8181 \
  -e DEPLOY_REF=${TARGET_COMMIT} \
  ${REGISTRY_IMAGE}:sha-${TARGET_COMMIT}

echo "DEPLOY_REF=${TARGET_COMMIT}" | sudo tee /home/qzm/Desktop/catty-reminders-app/.env.deploy

echo "> Container deployed successfully!"
