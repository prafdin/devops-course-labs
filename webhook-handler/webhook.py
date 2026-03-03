#!/usr/bin/env python3
"""
Обработчик вебхуков GitHub - Полная версия с перезапуском приложения
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import subprocess
import os
import threading
import time

# Конфигурация
REPO_URL = "https://github.com/goganizmrulit40/catty-reminders-app.git"
APP_DIR = "/opt/catty-reminders-app"
LOG_FILE = "/var/log/webhook.log"
BRANCH = "lab1"

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def restart_app():
    """Перезапуск приложения"""
    try:
        logging.info("Перезапуск приложения...")
        subprocess.run(["sudo", "systemctl", "restart", "catty-reminders"], check=True)
        
        # Ждем запуска приложения
        time.sleep(3)
        
        # Проверяем, запустилось ли приложение
        result = subprocess.run(
            ["curl", "-f", "http://localhost:8181/health"],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logging.info("Приложение успешно перезапущено")
            return True
        else:
            logging.error("Приложение не запустилось")
            return False
    except Exception as e:
        logging.error(f"Не удалось перезапустить приложение: {e}")
        return False

def install_dependencies():
    """Установка Python зависимостей"""
    try:
        requirements_file = os.path.join(APP_DIR, "requirements.txt")
        if os.path.exists(requirements_file):
            logging.info("Установка зависимостей...")
            subprocess.run(["pip3", "install", "-r", requirements_file], check=True)
            logging.info("Зависимости успешно установлены")
            return True
        else:
            logging.info("Файл requirements.txt не найден")
            return True
    except Exception as e:
        logging.error(f"Не удалось установить зависимости: {e}")
        return False

def update_code():
    """Клонирование или обновление репозитория"""
    try:
        if not os.path.exists(APP_DIR):
            logging.info("Клонирование репозитория...")
            subprocess.run([
                "git", "clone", "-b", BRANCH, "--single-branch", REPO_URL, APP_DIR
            ], check=True)
            logging.info("Репозиторий успешно склонирован")
        else:
            logging.info("Обновление репозитория...")
            os.chdir(APP_DIR)
            subprocess.run(["git", "fetch", "origin"], check=True)
            subprocess.run(["git", "reset", "--hard", f"origin/{BRANCH}"], check=True)
            logging.info("Репозиторий успешно обновлен")
        
        # Получаем текущий коммит
        os.chdir(APP_DIR)
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True
        )
        commit_hash = result.stdout.strip()
        logging.info(f"Текущий коммит: {commit_hash}")
        
        # Устанавливаем зависимости
        install_dependencies()
        
        # Перезапускаем приложение
        restart_app()
        
        return True, commit_hash
    except Exception as e:
        logging.error(f"Не удалось обновить код: {e}")
        return False, None

class WebhookHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """Обработка POST запросов"""
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
                
                if branch == BRANCH:
                    # Получаем информацию о коммитах
                    commits = payload.get('commits', [])
                    if commits:
                        last_commit = commits[-1]
                        commit_msg = last_commit.get('message', '')
                        logging.info(f"Сообщение коммита: {commit_msg}")
                    
                    # Запускаем обновление в фоне
                    thread = threading.Thread(target=update_code)
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
    print("Нажмите Ctrl+C для остановки")
    server.serve_forever()

if __name__ == '__main__':
    run()
