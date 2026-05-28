#!/bin/bash
set -e

DEPLOY_PORT=${DEPLOY_PORT:-22}
CONTAINER_NAME="catty-app"
PORT="8181"
IMAGE="$IMAGE_NAME:$RELEASE_HASH"

SSH_OPTIONS="-p $DEPLOY_PORT -o StrictHostKeyChecking=no"

ssh $SSH_OPTIONS "$DEPLOY_USER@$DEPLOY_HOST" << EOF
  set -e
  echo "$DOCKER_TOKEN" | sudo docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
  sudo docker pull "$IMAGE"
  sudo docker stop "$CONTAINER_NAME" || true
  sudo docker rm "$CONTAINER_NAME" || true
  sudo docker run -d \
    -p "$PORT:$PORT" \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -v /home/qzm/Desktop/catty-reminders-app/config.json:/app/config.json \
    -e DEPLOY_REF="$RELEASE_HASH" \
    "$IMAGE"
  sleep 5
  if sudo docker ps | grep -q "$CONTAINER_NAME"; then
    echo "Success"
  else
    sudo docker logs "$CONTAINER_NAME"
    exit 1
  fi
EOF
