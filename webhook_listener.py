import os
import subprocess
import threading
import logging
from flask import Flask, request, jsonify

APP_DIR = "/home/hesa/catty-reminders-app"
ENV_VARS_FILE = "/etc/catty-app-env"
SERVICE_NAME = "catty"
LOG_FILE = "/home/hesa/webhook-handler/deploy.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

def perform_deployment(commit_hash):
    try:
        subprocess.run(["git", "-C", APP_DIR, "fetch", "--all"], check=True)
        subprocess.run(["git", "-C", APP_DIR, "reset", "--hard", commit_hash], check=True)
        with open(ENV_VARS_FILE, "w") as f:
            f.write(f"DEPLOY_REF={commit_hash}\n")
        subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME], check=True)
        logging.info(f"Деплой успешен: {commit_hash}")
    except Exception as e:
        logging.error(f"Ошибка деплоя: {e}")

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('X-GitHub-Event') == 'push':
        payload = request.get_json()
        commit_sha = payload.get('after')
        if commit_sha and commit_sha != "0000000000000000000000000000000000000000":
            threading.Thread(target=perform_deployment, args=(commit_sha,)).start()
            return jsonify({"status": "accepted"}), 202
    return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
