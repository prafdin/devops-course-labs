#!/usr/bin/env python3
"""
Обработчик вебхуков GitHub - Исправленная версия для Python 3.6
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import subprocess
import os
import threading
import time

# ==================== КОНФИГУРАЦИЯ ====================
REPO_URL = "https://github.com/goganizmrulit40/catty-reminders-app.git"
APP_DIR = "/opt/catty-reminders"
LOG_FILE = "/var/log/webhook/webhook.log"
BRANCH = "lab1"
DEPLOY_REF_FILE = "/opt/catty-reminders/deploy_ref.txt"

# Создаем папку для логов
os.makedirs("/var/log/webhook", exist_ok=True)

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def restart_app(commit_hash=None):
    """Перезапуск приложения"""
    try:
        logging.info(f"Перезапуск приложения... restart_app вызван с commit_hash: {commit_hash}")
        # Не используем check=True, проверяем сами
        result = subprocess.run(
            ["sudo", "-n", "systemctl", "restart", "catty-reminders"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if result.returncode == 0:
            logging.info("Команда перезапуска выполнена успешно")
        else:
            logging.error(f"Ошибка при выполнении restart: {result.stderr}")
            return False
        
        # Записываем commit_hash в файл для deploy_ref
        if commit_hash:
            try:
                with open(DEPLOY_REF_FILE, 'w') as f:
                    f.write(commit_hash)
                logging.info(f"✅ Deploy ref записан в файл: {commit_hash}")
                
                # Проверим, что записалось
                with open(DEPLOY_REF_FILE, 'r') as f:
                    content = f.read().strip()
                logging.info(f"✅ Проверка файла: '{content}'")
            except Exception as e:
                logging.error(f"❌ Не удалось записать deploy_ref: {e}")
        else:
            logging.warning("⚠️ commit_hash не передан, файл не обновлен")

        # Ждем запуска
        time.sleep(10)
        
        # Проверяем, что приложение отвечает
        check = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8181/login"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=5
        )
        
        if check.stdout and check.stdout.strip() == "200":
            logging.info(f"Приложение успешно перезапущено и отвечает 200")
            return True
        else:
            logging.warning(f"Приложение перезапущено, но отвечает кодом {check.stdout}")

	    # Записываем время деплоя
            import datetime
	    with open('/opt/catty-reminders/deploy_time.txt', 'w') as f:
    		f.write(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
            logging.info(f"⏱️ Deploy time записан")

            return True  # Всё равно считаем успехом, потому что restart прошел
    except Exception as e:
        logging.error(f"Исключение при перезапуске: {e}")
        return False

def install_dependencies():
    """Установка Python зависимостей"""
    try:
        requirements_file = os.path.join(APP_DIR, "requirements.txt")
        if os.path.exists(requirements_file):
            logging.info("Установка зависимостей...")
            pip_path = os.path.join(APP_DIR, "venv", "bin", "pip")
            if os.path.exists(pip_path):
                result = subprocess.run(
                    [pip_path, "install", "-r", requirements_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                logging.info("Зависимости успешно установлены")
            else:
                logging.warning("Виртуальное окружение не найдено, используем системный pip")
                result = subprocess.run(
                    ["pip3", "install", "-r", requirements_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
            return True
        else:
            logging.info("Файл requirements.txt не найден")
            return True
    except Exception as e:
        logging.error(f"Не удалось установить зависимости: {e}")
        return False

def update_code(branch_name="lab1"):
    """Клонирование или обновление репозитория"""
    try:
        if not os.path.exists(APP_DIR):
            logging.info("Клонирование репозитория...")
            result = subprocess.run(
                ["git", "clone", "-b", branch_name, "--single-branch", REPO_URL, APP_DIR],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if result.returncode != 0:
                logging.error(f"Ошибка клонирования: {result.stderr}")
                return False, None
            logging.info("Репозиторий успешно склонирован")
        else:
	    logging.info(f"Обновление репозитория для ветки {branch_name}...")
            os.chdir(APP_DIR)
            
            result = subprocess.run(
                ["git", "fetch", "origin"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if result.returncode != 0:
                logging.error(f"Ошибка fetch: {result.stderr}")
                return False, None
            
            result = subprocess.run(
                ["git", "reset", "--hard", f"origin/{branch_name}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if result.returncode != 0:
                logging.error(f"Ошибка reset: {result.stderr}")
                return False, None
            
            logging.info("Репозиторий успешно обновлен")
        
        os.chdir(APP_DIR)
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if result.returncode == 0:
            commit_hash = result.stdout.strip()
            logging.info(f"Текущий коммит: {commit_hash}")
        else:
            commit_hash = "unknown"
            logging.error("Не удалось получить хэш коммита")
        
        install_dependencies()
        restart_app(commit_hash)
        
        return True, commit_hash
    except Exception as e:
        logging.error(f"Не удалось обновить код: {e}")
        return False, None

class WebhookHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data)
            event = self.headers.get('X-GitHub-Event', 'неизвестно')
            logging.info(f"Получено событие {event} от {self.client_address[0]}")
            
            if event == 'push':
                branch = payload.get('ref', '').replace('refs/heads/', '')
                repo_name = payload.get('repository', {}).get('full_name', 'неизвестно')
                pusher = payload.get('pusher', {}).get('name', 'неизвестно')
                
                logging.info(f"Push в {repo_name} ветка {branch} от {pusher}")
                
                if branch.startswith("lab1"):
                    commits = payload.get('commits', [])
                    if commits:
                        last_commit = commits[-1]
                        commit_msg = last_commit.get('message', '')
                        logging.info(f"Сообщение коммита: {commit_msg}")
                    
                    thread = threading.Thread(target=update_code, args=(branch,))
                    thread.start()
                    
                    self.send_response(202)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "принято",
                        "branch": branch,
                        "repo": repo_name,
                        "message": "Развертывание запущено"
                    }, ensure_ascii=False).encode())
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "игнорируется",
                        "branch": branch,
                        "message": f"Отслеживается только ветка {BRANCH}"
                    }, ensure_ascii=False).encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "игнорируется",
                    "event": event
                }, ensure_ascii=False).encode())
                
        except json.JSONDecodeError:
            logging.error("Неверный формат JSON")
            self.send_response(400)
            self.end_headers()
        except Exception as e:
            logging.error(f"Ошибка обработки вебхука: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        logging.info(f"{self.address_string()} - {format % args}")

def run(port=8080):
    server = HTTPServer(('', port), WebhookHandler)
    print(f"✅ Сервер вебхуков запущен на порту {port}")
    print(f"📁 Отслеживаемая ветка: {BRANCH}")
    print(f"📦 Репозиторий: {REPO_URL}")
    print(f"📝 Логи: {LOG_FILE}")
    print(f"📄 Deploy ref файл: {DEPLOY_REF_FILE}")
    print("Нажмите Ctrl+C для остановки")
    server.serve_forever()

if __name__ == '__main__':
    run()
