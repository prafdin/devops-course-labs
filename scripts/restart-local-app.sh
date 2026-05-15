#!/usr/bin/env bash
pkill -f "uvicorn app.main:app" || true
nohup venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8181 > .uvicorn.log 2>&1 &
