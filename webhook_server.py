from flask import Flask, request, jsonify
import subprocess
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

REPO_PATH = "/home/ubuntu/devops-lab/app"
APP_PORT = 8181

@app.route('/', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'GET':
        return "Webhook server is running", 200

    logging.info("Получен POST запрос от GitHub")
    
    # 1. Обновляем код (если используешь git)
    if os.path.exists(os.path.join(REPO_PATH, '.git')):
        subprocess.run(["git", "-C", REPO_PATH, "pull"], check=False)
    
    # 2. Перезапускаем приложение на порту 8181
    logging.info(f"Запуск приложения на порту {APP_PORT}...")
    subprocess.run(["pkill", "-f", f"python3.*app_server.py"], check=False)
    
    # Запускаем в фоне
    subprocess.Popen(
        ["python3", f"{REPO_PATH}/app_server.py", str(APP_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=REPO_PATH
    )
    
    logging.info("Приложение успешно развернуто")
    return jsonify({"status": "deployed"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
