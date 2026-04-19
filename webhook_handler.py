#!/usr/bin/env python3

import subprocess
import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

REPO_PATH = "/home/aleksandr/catty-reminders-app"
SERVICE_NAME = "catty-app"
VENV_PYTHON = f"{REPO_PATH}/venv/bin/python"
UVICORN_CMD = f"{VENV_PYTHON} -m uvicorn app.main:app --host 0.0.0.0 --port 8181"

@app.route('/', methods=['POST'])
def webhook():
    event_type = request.headers.get('X-GitHub-Event', '')
    if event_type != 'push':
        print(f"Ignored event: {event_type}")
        return jsonify({"status": "ignored"}), 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON"}), 400

    sha = data.get('after')
    if not sha or sha == '0'*40:
        return jsonify({"error": "Invalid SHA"}), 400

    ref = data.get('ref', '')
    branch = ref.split('/')[-1] if ref else 'main'

    print(f"=== Webhook received ===")
    print(f"Branch: {branch}")
    print(f"Commit: {sha}")

    try:
        subprocess.run(
            f"cd {REPO_PATH} && git fetch origin && git checkout {branch} && git reset --hard {sha}",
            shell=True, check=True, capture_output=True, text=True
        )
        print("Git update OK")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr}")
        return jsonify({"error": "Git update failed"}), 500

    subprocess.run(f"{REPO_PATH}/venv/bin/pip install -r {REPO_PATH}/requirements.txt", shell=True)

    env_path = f"{REPO_PATH}/.env"
    with open(env_path, 'a') as f:
        f.write(f"\nDEPLOY_REF={sha}\n")

    if SERVICE_NAME:
        subprocess.run(f"sudo systemctl restart {SERVICE_NAME}", shell=True)
    else:
        subprocess.run("pkill -f 'uvicorn.*app.main:app' || true", shell=True)
        subprocess.run(
            f"cd {REPO_PATH} && nohup {UVICORN_CMD} > /tmp/catty.log 2>&1 &",
            shell=True
        )

    print("Deployment finished")
    return jsonify({"status": "success", "commit": sha}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive"}), 200

@app.route('/', methods=['GET'])
def index():
    return "Webhook handler for Catty (FastAPI) is running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
