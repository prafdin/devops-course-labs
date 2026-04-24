import os
import subprocess
import threading
import logging
from flask import Flask, request, jsonify

# Пути под твоего пользователя
REPO_DIR = "/home/umarbis/catty-reminders-app"
ENV_FILE = "/etc/catty-app-env"
SERVICE = "catty"

app = Flask(__name__)
logging.basicConfig(filename="/home/umarbis/deploy.log", level=logging.INFO)

def run_deploy(sha):
    try:
        # 1. Обновляем код
        subprocess.run(["git", "-C", REPO_DIR, "fetch", "--all"], check=True)
        subprocess.run(["git", "-C", REPO_DIR, "reset", "--hard", sha], check=True)
        # 2. Пишем хэш для GitHub Actions
        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={sha}\n")
        # 3. Перезапускаем сайт
        subprocess.run(["sudo", "systemctl", "restart", SERVICE], check=True)
        logging.info(f"Success: {sha}")
    except Exception as e:
        logging.error(f"Error: {e}")

@app.route('/', methods=['POST'])
def handle():
    if request.headers.get('X-GitHub-Event') == 'push':
        sha = request.json.get('after')
        if sha and sha != "0000000000000000000000000000000000000000":
            threading.Thread(target=run_deploy, args=(sha,)).start()
            return jsonify({"status": "ok"}), 202
    return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
