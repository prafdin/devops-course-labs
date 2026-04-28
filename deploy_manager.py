import os
import logging
import subprocess
from threading import Thread
from flask import Flask, request, jsonify

CONFIG = {
    "repo_dir": "/home/password_123/catty-reminders-app",
    "env_path": "/etc/catty-app-env",
    "systemd_unit": "catty",
    "log_file": "/home/password_123/deploy.log" 
}

app = Flask(__name__)

# Иная настройка логирования
logger = logging.getLogger("DeployLogger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(CONFIG["log_file"])
file_handler.setFormatter(logging.Formatter('%(levelname)s | %(name)s | %(message)s'))
logger.addHandler(file_handler)

class DeploymentEngine:
    """Класс для управления процессом обновления"""
    
    @staticmethod
    def sync_and_restart(commit_hash):
        logger.info(f"== Starting update pipeline for {commit_hash} ==")
        
        try:
            # 1. Синхронизация репозитория
            target = CONFIG["repo_dir"]
            subprocess.run(f"git -C {target} fetch --all", shell=True, check=True)
            subprocess.run(f"git -C {target} reset --hard {commit_hash}", shell=True, check=True)
            
            # 2. Запись данных для GitHub Actions (используем другой способ записи)
            # Вместо контекстного менеджера python используем системный echo через sudo
            sha_cmd = f"echo 'DEPLOY_REF={commit_hash}' | sudo tee {CONFIG['env_path']}"
            subprocess.run(sha_cmd, shell=True, check=True)
            
            # 3. Перезапуск основного демона
            unit = CONFIG["systemd_unit"]
            subprocess.run(f"sudo systemctl restart {unit}", shell=True, check=True)
            
            logger.info("== Application successfully refreshed ==")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.cmd}")
        except Exception as ex:
            logger.error(f"Unexpected deployment failure: {ex}")

@app.route('/', methods=['POST'])
def receive_payload():
    # Проверка заголовков GitHub
    gh_event = request.headers.get('X-GitHub-Event', '')
    
    if gh_event == 'ping':
        return jsonify({"status": "ready"}), 200
        
    if gh_event == 'push':
        body = request.get_json()
        # Извлекаем хэш. Поле 'after' - стандарт для push событий
        sha = body.get('after')
        
        # Проверка на пустой хэш (бывает при удалении веток)
        if sha and sha != "0000000000000000000000000000000000000000":
            logger.info(f"Push detected. Target SHA: {sha}")
            
            # Запуск логики обновления в фоновом потоке
            worker = Thread(target=DeploymentEngine.sync_and_restart, args=(sha,))
            worker.daemon = True
            worker.start()
            
            return jsonify({
                "accepted": True, 
                "ref": sha,
                "info": "Job sent to background"
            }), 202

    return jsonify({"accepted": False, "reason": "not a push event"}), 200

if __name__ == '__main__':
    # Слушаем на 8080 для FRP
    app.run(host='0.0.0.0', port=8080, debug=False)

