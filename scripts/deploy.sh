#!/bin/bash
set -e

REPO_LOWER=$(echo "$REPO" | tr '[:upper:]' '[:lower:]')
IMAGE="ghcr.io/${REPO_LOWER}:${RELEASE_HASH}"

echo "Deploying: $IMAGE"

ssh -i ~/.ssh/id_rsa \
  -o StrictHostKeyChecking=no \
  "${DEPLOY_USER}@${DEPLOY_HOST}" << EOF

set -e

echo "Login GHCR"
echo "${GH_TOKEN}" | docker login ghcr.io \
  -u "${GH_USER}" \
  --password-stdin

echo "Pull image"
docker pull ${IMAGE}

echo "Stop old container"
docker stop catty-app || true
docker rm catty-app || true

echo "Start new container"
docker run -d \
  --name catty-app \
  --restart unless-stopped \
  -p 8181:8181 \
  -e COMMIT_SHA=${RELEASE_HASH} \
  ${IMAGE}

docker ps
echo "DEPLOY OK"
EOF
