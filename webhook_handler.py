#!/usr/bin/env python3

import os
import json
import subprocess
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

def load_env():
    env_file = "/home/Roman/Desktop/catty-reminders-app/.env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/Roman/Desktop/catty-reminders-app/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

PROJECT_PATH = os.getenv('PROJECT_PATH', '/home/Roman/Desktop/catty-reminders-app')
REPO_URL = os.getenv('REPO_URL', 'https://github.com/RenTogan/catty-reminders-app.git')
PORT = int(os.getenv('WEBHOOK_PORT', '8080'))
BRANCH = os.getenv('BRANCH', 'lab1')

class CustomWebhookHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        logger.info(f"Запрос: {args}")
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = json.dumps({
                "status": "alive",
                "timestamp": datetime.now().isoformat(),
                "project": "catty-reminders-app",
                "owner": "RenTogan",
                "branch": BRANCH
            })
            self.wfile.write(status.encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"""
            <html>
            <head><title>Webhook Service - catty-reminders</title></head>
            <body style="font-family: Arial; text-align: center; margin-top: 50px;">
                <h1>Webhook Service Active</h1>
                <p>Project: catty-reminders-app</p>
                <p>Owner: RenTogan</p>
                <p>Branch: {BRANCH}</p>
                <p>Port: {PORT}</p>
                <p>Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
                <small>GitHub webhook endpoint: POST /webhook</small>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
    
    def do_POST(self):
        if self.path == '/webhook':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                event_type = self.headers.get('X-GitHub-Event', 'unknown')
                payload = json.loads(post_data.decode('utf-8'))
                
                logger.info(f"Получено событие: {event_type}")
                
                if event_type == 'push':
                    self.handle_push_event(payload)
                elif event_type == 'ping':
                    self.handle_ping_event(payload)
                else:
                    logger.info(f"Игнорируем событие типа: {event_type}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "accepted"}')
                
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON: {e}")
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "invalid json"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_push_event(self, payload):
        try:
            branch = payload.get('ref', '').replace('refs/heads/', '')
            repository = payload.get('repository', {}).get('name', 'unknown')
            sender = payload.get('sender', {}).get('login', 'unknown')
            commits = len(payload.get('commits', []))
            
            logger.info(f"Push в ветку {branch} от {sender}, коммитов: {commits}")
            
            
            if branch in ['main', 'master']:
                logger.info(f"Пропускаем деплой для ветки {branch}")
                return
            
            self.run_deployment(branch)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке push события: {e}")
    
    def handle_ping_event(self, payload):
        hook_id = payload.get('hook_id', 'unknown')
        logger.info(f"Ping получен от GitHub, hook_id: {hook_id}")
    
    def run_deployment(self, branch):
        deploy_script = os.path.join(PROJECT_PATH, "deploy_app.sh")
        
        if not os.path.exists(deploy_script):
            logger.error(f"Скрипт развертывания не найден: {deploy_script}")
            return
        
        logger.info(f"Запуск развертывания для ветки {branch}")
        
        try:
            result = subprocess.run(
                [deploy_script, branch],
                cwd=PROJECT_PATH,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"Развертывание успешно завершено")
                logger.debug(f"Вывод скрипта: {result.stdout}")
            else:
                logger.error(f"Ошибка при развертывании. Код: {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Таймаут при выполнении скрипта развертывания")
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")

def main():
    logger.info("=" * 50)
    logger.info(f"Запуск webhook сервера для {REPO_URL}")
    logger.info(f"Порт: {PORT}")
    logger.info(f"Ветка: {BRANCH}")
    logger.info(f"Путь к проекту: {PROJECT_PATH}")
    logger.info("=" * 50)
    
    server = HTTPServer(('0.0.0.0', PORT), CustomWebhookHandler)
    
    try:
        logger.info("Сервер запущен. Ожидание webhook запросов...")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки. Завершение работы...")
        server.shutdown()
        logger.info("Сервер остановлен")

if __name__ == '__main__':
    main()
