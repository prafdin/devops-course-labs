#!/bin/bash

set -e

REPO_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

IMAGE="ghcr.io/${REPO_LOWER}:${RELEASE_HASH}"

echo "Deploying image:"
echo "$IMAGE"

ssh -p "${DEPLOY_PORT}" \
    -o StrictHostKeyChecking=no \
    "${DEPLOY_USER}@${DEPLOY_HOST}" << EOF

set -e

echo "> Login to GHCR"

echo "${DOCKER_TOKEN}" | docker login ghcr.io \
    -u "${GITHUB_ACTOR}" \
    --password-stdin

echo "> Pull image"

docker pull ${IMAGE}

echo "> Stop old container"

docker stop catty-app || true
docker rm catty-app || true

echo "> Start new container"

docker run -d \
    --name catty-app \
    --restart unless-stopped \
    -p 8181:8181 \
    -e COMMIT_SHA=${RELEASE_HASH} \
    ${IMAGE}

sleep 5

docker ps

echo "> Deploy successful"

EOF
