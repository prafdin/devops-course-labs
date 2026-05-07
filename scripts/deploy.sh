#!/bin/bash
set -e

if [ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ] || [ -z "$RELEASE_HASH" ]; then
    echo "Error: Required environment variables are not set"
    exit 1
fi

REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')
IMAGE="ghcr.io/${REPO_LOWER}:${RELEASE_HASH}"

ssh -p "${DEPLOY_PORT:-22}" -o StrictHostKeyChecking=no "${DEPLOY_USER}@${DEPLOY_HOST}" "bash -s" << EOF
    set -e
    
    echo "> Logging in to GHCR..."
    echo "${DOCKER_TOKEN}" | docker login ghcr.io -u "${GITHUB_ACTOR}" --password-stdin
    
    echo "> Pulling image: ${IMAGE}"
    docker pull ${IMAGE}
    
    echo "> Restarting container..."
    docker stop catty-app || true
    docker rm catty-app || true
    
    docker run -d \
        --name catty-app \
        --restart unless-stopped \
        -p 8181:8181 \
        -e COMMIT_SHA=${RELEASE_HASH} \
        ${IMAGE}
    
    sleep 2

    echo "> Injecting hash into HTML file..."
    docker exec catty-app sed -i "s/content=\"NA\"/content=\"${RELEASE_HASH}\"/g" /app/templates/login.html
    
    echo "> Deployment successful!"
EOF
