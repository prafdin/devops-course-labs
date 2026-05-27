#!/bin/bash
set -e

cd /home/qzm/Desktop/catty-reminders-app

docker compose pull
docker compose down --volumes --remove-orphans || true
docker ps -a --filter "name=catty" -q | xargs -r docker rm -f
docker compose up -d --remove-orphans
docker system prune -f
