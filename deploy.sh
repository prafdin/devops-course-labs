#!/bin/bash
set -e
COMMIT_SHA=$1
echo "Deploying image with SHA: $COMMIT_SHA"
export IMAGE_TAG=$COMMIT_SHA
docker compose pull
docker compose up -d
