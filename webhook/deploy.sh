#!/bin/bash

BRANCH=$1
echo "=== deploy: $BRANCH ==="
echo "Current directory: $(pwd)"

# Копируем или синхронизируем изменения в основную директорию
TARGET_DIR="/home/ubuntu/devops/catty-reminders-app"

echo "Syncing changes to $TARGET_DIR..."

# Синхронизируем файлы (игнорируя .git)
rsync -av --exclude='.git' ./ $TARGET_DIR/ --update 2>/dev/null || cp -r . $TARGET_DIR/

echo "✅ Deployment completed!"
exit 0
