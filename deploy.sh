#!/bin/bash
set -e
IMAGE_NAME=$1
DEPLOY_REF=$2
HOST_PORT=8181
CONTAINER_PORT=8181
CONTAINER_NAME="catty-reminders-app"
IMAGE="$IMAGE_NAME:$DEPLOY_REF"
echo "=== DEPLOY релиза ==="
echo "Текущий SHA релиза: $DEPLOY_REF"
docker pull $IMAGE
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true
docker run -d -p $HOST_PORT:$CONTAINER_PORT --name $CONTAINER_NAME --restart unless-stopped $IMAGE
