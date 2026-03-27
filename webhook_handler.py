import os
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

PORT = 8080
PROJECT_DIR = os.path.expanduser("~/my_project")
APP_SERVICE = "my_app.service"

class WebhookHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Обработка POST запросов от GitHub"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode('utf-8'))
            event_type = self.headers.get('X-GitHub-Event', 'unknown')
            
            print(f"\nСобытие: {event_type} | Время: {datetime.now().strftime('%H:%M:%S')}")

            if event_type == 'push':
                self._handle_push(payload)
            else:
                print(f"Пропускаем событие '{event_type}'")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "processed"}')

        except Exception as e:
            print(f"❌Ошибка: {e}")
            self.send_response(500)
            self.end_headers()

    def _handle_push(self, payload):
        """Логика автоматического развертывания"""
        ref = payload.get('ref', '')
        branch = ref.replace('refs/heads/', '')
        
        print(f"Push в ветку: {branch}")
        
        try:
            os.chdir(PROJECT_DIR)
            
            print("Обновление кода...")
            subprocess.run(["git", "fetch", "origin"], check=True)
            subprocess.run(["git", "checkout", branch], check=True)
            subprocess.run(["git", "pull", "origin", branch], check=True)

            print(f"Перезапуск {APP_SERVICE}...")
            subprocess.run(["sudo", "systemctl", "restart", APP_SERVICE], check=True)
            
            print("✅Развертывание завершено успешно!")

        except subprocess.CalledProcessError as e:
            print(f"❌Ошибка при выполнении команды: {e}")

    def do_GET(self):
        """Страница статуса"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = f"""
        <html>
            <body style="font-family: sans-serif; padding: 50px;">
                <h1>🚀 Webhook Handler Status</h1>
                <p><b>Статус:</b> Ожидание событий от GitHub</p>
                <p><b>Порт:</b> {PORT}</p>
                <p><b>Проект:</b> {PROJECT_DIR}</p>
            </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    print(f"🚀 Запуск обработчика на порту {PORT}...")
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    server.serve_forever()
