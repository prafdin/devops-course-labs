#!/bin/bash

set -e

if[ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ]; then
    echo "Error: DEPLOY_HOST and DEPLOY_USER must be set"
    exit 1
fi

DEPLOY_PORT=${DEPLOY_PORT:-22}
IMAGE_NAME=${IMAGE_NAME,,}
TARGET_DIR="~/catty-app"

echo "Deploying to $DEPLOY_HOST:$DEPLOY_PORT"
echo "Image: $IMAGE_NAME:$RELEASE_HASH"

SSH_OPTIONS="-p $DEPLOY_PORT -o StrictHostKeyChecking=no"

ssh $SSH_OPTIONS "$DEPLOY_USER@$DEPLOY_HOST" "mkdir -p $TARGET_DIR"

scp $SSH_OPTIONS docker-compose.yaml "$DEPLOY_USER@$DEPLOY_HOST:$TARGET_DIR/docker-compose.yaml"

ssh $SSH_OPTIONS "$DEPLOY_USER@$DEPLOY_HOST" << EOF
    set -e
    
    cd $TARGET_DIR
    
    echo "Logging in to GitHub Container Registry..."
    echo "$DOCKER_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
    
    # Экспортируем переменные, которые подхватит docker-compose.yaml
    export IMAGE_NAME="$IMAGE_NAME"
    export IMAGE_TAG="$RELEASE_HASH"
    
    echo "Pulling new images..."
    docker compose pull
    
    echo "Starting containers..."
    # --remove-orphans удалит старые standalone контейнеры, если они остались
    docker compose up -d --remove-orphans
    
    sleep 5
    
    # Проверка, что сервис app успешно запущен
    if docker compose ps | grep -q "Up"; then
        echo "Deployment completed successfully"
    else
        echo "ERROR: Application failed to start"
        docker compose logs
        exit 1
    fi
EOF