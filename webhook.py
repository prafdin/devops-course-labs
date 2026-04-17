#!/usr/bin/env python3

import subprocess
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
REPO_PATH = '/home/yaroslav/devops-lab/catty-reminders-app'

class WebhookHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body.decode('utf-8'))
            
            event_type = self.headers.get('X-GitHub-Event', 'unknown')
            repo_name = payload.get('repository', {}).get('full_name', 'unknown')
            branch = payload.get('ref', '').replace('refs/heads/', '')
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n [{timestamp}] Webhook: {event_type} - {repo_name} - {branch}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            
            if event_type == 'push':
                self._deploy(branch)
            return
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            
        except Exception as e:
            print(f" Ошибка: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f"""
        <h1> Webhook Server Active</h1>
        <p>Время: {datetime.now()}</p>
        <p>Порт: {PORT}</p>
        <p>Приложение: Catty Reminders</p>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def _deploy(self, branch):
        print(f"    Деплой ветки: {branch}")
        
        # git pull
        print(f"    Обновление кода...")
        subprocess.run(['git', 'fetch', '--all'], cwd=REPO_PATH)
        subprocess.run(['git', 'checkout', branch], cwd=REPO_PATH)
        subprocess.run(['git', 'pull', 'origin', branch], cwd=REPO_PATH)
                # Запуск тестов (требование лабы)
        print(f"    Запуск тестов...")
        test_result = subprocess.run(
            [f'{REPO_PATH}/venv/bin/pytest', 'tests/', '--tb=short', '-q'],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        if test_result.returncode == 0:
            print(f"    Тесты прошли успешно!")
        else:
            print(f"    Тесты упали, но деплой продолжается (по условию лабы)")
            if test_result.stdout:
                print(f"   {test_result.stdout[:200]}...")


        # Устанавливаем зависимости
        print(f"    Проверка зависимостей...")
        subprocess.run([f'{REPO_PATH}/venv/bin/pip', 'install', '-r', 'requirements.txt'], cwd=REPO_PATH)
        
        # Перезапускаем uvicorn
        print(f"    Перезапуск приложения...")
        subprocess.run(['pkill', '-f', 'uvicorn app.main:app'], capture_output=True)
        subprocess.Popen(
            [f'{REPO_PATH}/venv/bin/uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8181'],
            cwd=REPO_PATH,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f"    Деплой завершен!")
    
    def log_message(self, format, *args):
        pass

def main():
    print(f" Запуск Webhook сервера на порту {PORT}")
    print(f" Репозиторий: {REPO_PATH}")
    print(f" {datetime.now()}")
    print(f"\n Ожидание webhook...\n")
    
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n Сервер остановлен")

if __name__ == '__main__':
    main()
