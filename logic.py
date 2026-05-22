import os
import subprocess
import threading
import logging
from flask import Flask, request, jsonify

REPO_DIR = "/home/kali/catty-reminders-app"
ENV_FILE = "/etc/catty-app-env"
SERVICE = "catty"

app = Flask(__name__)
logging.basicConfig(
    filename="/home/kali/deploy.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_deploy(sha):
    try:
        logging.info(f"Starting deploy for SHA: {sha}")
        
        # 1. Получаем последние изменения
        subprocess.run(["git", "-C", REPO_DIR, "fetch", "--all"], check=True, capture_output=True, text=True)
        
        # 2. Проверяем, существует ли коммит
        result = subprocess.run(["git", "-C", REPO_DIR, "cat-file", "-t", sha], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Commit {sha} not found in repository")
            return
        
        # 3. Сбрасываем до нужного коммита
        subprocess.run(["git", "-C", REPO_DIR, "reset", "--hard", sha], check=True, capture_output=True, text=True)
        
        # 4. Записываем SHA в файл окружения
        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={sha}\n")
            f.write(f"DEPLOY_TIME={subprocess.run(['date', '-Iseconds'], capture_output=True, text=True).stdout.strip()}\n")
        logging.info(f"Wrote {sha} to {ENV_FILE}")
        
        # 5. Перезапускаем сервис
        result = subprocess.run(["sudo", "systemctl", "restart", SERVICE], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Successfully restarted {SERVICE}")
        else:
            logging.error(f"Failed to restart {SERVICE}: {result.stderr}")
        
        # 6. Проверяем статус сервиса
        status = subprocess.run(["sudo", "systemctl", "is-active", SERVICE], 
                               capture_output=True, text=True)
        logging.info(f"Service status: {status.stdout.strip()}")
        
        logging.info(f"Deploy completed successfully for {sha}")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e.cmd}, return code: {e.returncode}")
        logging.error(f"STDERR: {e.stderr}")
        logging.error(f"STDOUT: {e.stdout}")
    except Exception as e:
        logging.error(f"Deploy error: {e}", exc_info=True)

@app.route('/', methods=['POST'])
def handle():
    if request.headers.get('X-GitHub-Event') == 'push':
        sha = request.json.get('after')
        if sha and sha != "0000000000000000000000000000000000000000":
            logging.info(f"Received webhook for SHA: {sha}")
            threading.Thread(target=run_deploy, args=(sha,)).start()
            return jsonify({"status": "ok"}), 202
    return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
