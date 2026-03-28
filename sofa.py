#!/usr/bin/env python3
import os
import sys
import logging
import threading
import subprocess
from flask import Flask, request, jsonify

REPO_PATH = os.getenv('DEPLOY_REPO', '/home/password-123/catty-reminders-app')
ENV_FILE = os.getenv('DEPLOY_ENV_FILE', '/etc/catty-app-env')
SERVICE_NAME = os.getenv('DEPLOY_SERVICE', 'catty')
LOG_FILE = os.getenv('DEPLOY_LOG', '/home/password-123/deploy.log')
PORT = int(os.getenv('DEPLOY_PORT', 8080))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)
deploy_lock = threading.Lock()

def perform_deployment(commit_hash):
    with deploy_lock:
        logging.info(f"Starting deployment for {commit_hash}")
        try:
            subprocess.check_call(['git', '-C', REPO_PATH, 'fetch', '--all'])
            subprocess.check_call(['git', '-C', REPO_PATH, 'reset', '--hard', commit_hash])

            with open(ENV_FILE, 'w') as f:
                f.write(f"DEPLOY_REF={commit_hash}\n")

            subprocess.check_call(['sudo', 'systemctl', 'restart', SERVICE_NAME])

            logging.info(f"Deployment completed for {commit_hash}")
        except Exception as e:
            logging.error(f"Deployment error: {e}")

@app.route('/', methods=['POST'])
@app.route('/webhook', methods=['POST'])
def github_webhook():
    if request.headers.get('X-GitHub-Event') != 'push':
        return jsonify({'status': 'ignored'}), 200

    data = request.get_json()
    if not data:
        return jsonify({'status': 'error'}), 400

    commit_hash = data.get('after')
    if not commit_hash or commit_hash == '0000000000000000000000000000000000000000':
        return jsonify({'status': 'ignored'}), 200

    threading.Thread(target=perform_deployment, args=(commit_hash,)).start()
    return jsonify({'status': 'accepted'}), 202

# опционально (чтобы в браузере не было 404)
@app.route('/', methods=['GET'])
def index():
    return "ok"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
