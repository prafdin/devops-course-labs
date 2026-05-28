#!/bin/bash
set -e
cd /home/qzm/Desktop/catty-reminders-app || exit 1

echo "${{ secrets.DOCKER_TOKEN }}" | sudo docker login ghcr.io -u kuzminstanislav --password-stdin

TARGET_SHA="${{ github.sha }}"
echo "IMAGE=ghcr.io/kuzminstanislav/catty-reminders-app:$TARGET_SHA" > .env

sudo docker compose down --remove-orphans
sudo docker compose pull
sudo docker compose --env-file .env up -d

for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8181/ >/dev/null || curl -I http://127.0.0.1:8181/login 2>&1 | grep -q "405"; then
    echo "App is healthy"
    exit 0
  fi
  echo "Waiting for app... ($i/30)"
  sleep 5
done

sudo docker compose logs app
exit 1
