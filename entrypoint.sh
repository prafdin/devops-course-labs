#!/usr/bin/env sh
set -eu

if [ -f /app/config.compose.json ]; then
  cp /app/config.compose.json /app/config.json
fi

exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8181
