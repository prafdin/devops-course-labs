#!/usr/bin/env python3
"""
Webhook сервер для автоматического деплоя catty-reminders-app
"""

import subprocess
import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Конфигурация
PORT = 8080
DEPLOY_SCRIPT = os.path.expanduser("~/devops-lab/deploy.sh")

class WebhookHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Переопределяем логирование"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")
    
    def do_POST(self):
        """Обработка POST запросов от GitHub"""
        
        # Получаем размер данных
        content_length = int(self.headers.get('Content-Length', 0))
        
        # Читаем данные
        body = self.rfile.read(content_length)
        
        # Парсим JSON
        try:
            payload = json.loads(body.decode('utf-8'))
            self._process_webhook(payload)
            
            # Отвечаем успехом
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
            
        except json.JSONDecodeError:
            print(f"Ошибка парсинга JSON")
            self.send_response(400)
            self.end_headers()
        except Exception as e:
            print(f"Ошибка: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        """Health check"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "service": "webhook-handler"}')
            return
        
        # Страница статуса
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Webhook Handler</title></head>
        <body>
            <h1>Webhook Handler Active</h1>
            <p>Status: Running</p>
            <p>Port: {PORT}</p>
            <p>Time: {datetime.now()}</p>
            <hr>
            <p><a href="/health">Health Check</a></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def _process_webhook(self, payload):
        """Обработка webhook события"""
        
        event_type = self.headers.get('X-GitHub-Event', 'unknown')
        
        print(f"\nWebhook получен от GitHub")
        print(f"   Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Тип события: {event_type}")
        
        if event_type == 'ping':
            print(f"Ping от GitHub - все работает")
        elif event_type == 'push':
            self._handle_push_event(payload)
        else:
            print(f"Событие '{event_type}' игнорируется")
    
    def _handle_push_event(self, payload):
        """Обработка push события - запуск деплоя"""
    
        branch = payload.get('ref', '').replace('refs/heads/', '')
        pusher = payload.get('pusher', {}).get('name', 'unknown')
        commits = payload.get('commits', [])
        commit_sha = payload.get('after')  
    
        if commits:
            last_commit = commits[-1].get('id', 'unknown')[:8]
        else:
            last_commit = "unknown"
    
        print(f"\nPush в ветку: {branch}")
        print(f"Автор: {pusher}")
        print(f"Коммитов: {len(commits)}")
        print(f"Последний коммит: {last_commit}")
        print(f"Полный SHA: {commit_sha}")
        print(f"Запуск автоматического деплоя...")
    
        try:
            process = subprocess.Popen(
                [DEPLOY_SCRIPT, commit_sha],  
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            print(f"Деплой запущен (PID: {process.pid})")
        except Exception as e:
            print(f"Ошибка запуска деплоя: {e}")

def main():
    print("=" * 60)
    print("Webhook Handler для DevOps Lab")
    print("=" * 60)
    print(f"\nПорт: {PORT}")
    print(f"Webhook URL: http://0.0.0.0:{PORT}/webhook")
    print(f"Health: http://0.0.0.0:{PORT}/health")
    print(f"Деплой скрипт: {DEPLOY_SCRIPT}")
    print("\nОжидание webhook от GitHub...")
    print("=" * 60 + "\n")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\nСервер остановлен")

if __name__ == '__main__':
    main()
