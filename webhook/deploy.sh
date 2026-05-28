#!/bin/bash

echo "🚀 Начинаем развертывание приложения..."

cd webhook
source .venv/bin/activate
uvicorn ../app.main:app --reload --host 0.0.0.0 --port 8181