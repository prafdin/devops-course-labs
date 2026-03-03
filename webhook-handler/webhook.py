#!/usr/bin/env python3
"""
Обработчик вебхуков GitHub - Версия с клонированием репозитория
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import subprocess
import os
import threading

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

def clone_repository():
    """Клонирование или обновление репозитория"""
    try:
        if not os.path.exists(APP_DIR):
            logging.info("Клонирование репозитория...")
            subprocess.run([
                "git", "clone", "-b", BRANCH, "--single-branch", REPO_URL, APP_DIR
            ], check=True)
            logging.info("Репозиторий успешно склонирован")
        else:
            logging.info("Репозиторий уже существует")
        return True
    except Exception as e:
        logging.error(f"Не удалось клонировать репозиторий: {e}")
        return False

class WebhookHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """Обработка POST запросов"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data)
            event = self.headers.get('X-GitHub-Event', 'неизвестно')
            logging.info(f"Получено событие {event}")
            
            if event == 'push':
                branch = payload.get('ref', '').replace('refs/heads/', '')
                logging.info(f"Push в ветку: {branch}")
                
                if branch == BRANCH:
                    # Запускаем клонирование в фоне
                    thread = threading.Thread(target=clone_repository)
                    thread.start()
                    
                    self.send_response(202)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "принято",
                        "branch": branch
                    }, ensure_ascii=False).encode())
                else:
                    self.send_response(200)
                    self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        logging.info(f"{self.address_string()} - {format % args}")

def run(port=8080):
    server = HTTPServer(('', port), WebhookHandler)
    print(f"Сервер вебхуков запущен на порту {port}")
    server.serve_forever()

if __name__ == '__main__':
    run()
