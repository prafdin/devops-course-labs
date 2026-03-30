#!/bin/bash

set -e

if [ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ]; then
    echo "Error: DEPLOY_HOST and DEPLOY_USER must be set"
    exit 1
fi

if [ -z "$RELEASE_HASH" ]; then
    echo "Error: RELEASE_HASH must be set"
    exit 1
fi

if [ -z "$IMAGE_NAME" ]; then
    echo "Error: IMAGE_NAME must be set"
    exit 1
fi

DEPLOY_PORT=${DEPLOY_PORT:-22}
CONTAINER_NAME="catty-app"
PORT="8181"
IMAGE="$IMAGE_NAME:$RELEASE_HASH"

echo "Deploying to $DEPLOY_HOST:$DEPLOY_PORT"
echo "User: $DEPLOY_USER"
echo "Release hash: $RELEASE_HASH"
echo "Image: $IMAGE"

SSH_OPTIONS="-p $DEPLOY_PORT -o StrictHostKeyChecking=no"

ssh $SSH_OPTIONS "$DEPLOY_USER@$DEPLOY_HOST" << EOF
    set -e
    
    echo ">Logging in to GitHub Container Registry..."
    echo "$DOCKER_TOKEN" | sudo docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

    echo ">Pulling image: $IMAGE"
    sudo docker pull $IMAGE
    
    echo ">Stopping old container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    
    echo ">Starting new container..."
    sudo docker run -d \
        -p $PORT:$PORT \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -e DEPLOY_REF=$RELEASE_HASH \
        $IMAGE
    
    sleep 4
    
    if sudo docker ps | grep -q $CONTAINER_NAME; then
        echo "Deployment completed successfully"
    else
        echo "ERROR: Application failed to start"
        docker logs $CONTAINER_NAME
        exit 1
    fi
EOF
