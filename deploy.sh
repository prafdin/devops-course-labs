#!/bin/bash
set -e

if [[ -z "$REPO_LOWER" || -z "$RELEASE_HASH" ]]; then
    echo "Ошибка: Переменные REPO_LOWER или RELEASE_HASH не установлены."
    exit 1
fi

ssh -p "$SERVER_PORT" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" << REMOTE_SCRIPT
    set -e
    cd /home/${SERVER_USER}/Desktop/catty-reminders-app

    echo "REPO_LOWER=${REPO_LOWER}" > .env
    echo "RELEASE_HASH=${RELEASE_HASH}" >> .env

    docker compose pull
    docker compose up -d --remove-orphans --pull always
REMOTE_SCRIPT
