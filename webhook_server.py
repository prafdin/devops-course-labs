#!/usr/bin/env python3
import tempfile
import subprocess
import json
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
TARGET_BRANCH = "lab1"
PROJECT_DIR = "/home/light/Рабочий стол/web-app/catty-reminders-app"

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = "<html><body><h1>Webhook сервер работает. Жду POST запросов от GitHub...</h1></body></html>"
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode('utf-8'))
            response_body = b'{"status": "success"}'
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
            
            event_type = self.headers.get('X-GitHub-Event', 'unknown')
            if event_type == 'push':
                threading.Thread(target=self._handle_push_event, args=(payload,)).start()
            elif event_type == 'ping':
                print("\nПолучен тестовый PING от GitHub! Связь установлена.")
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()

    def _handle_push_event(self, payload):
        branch = payload.get('ref', '').replace('refs/heads/', '')
        commit_sha = payload.get('after', 'unknown')

        if not branch:
            return

        print(f"\nЗАПУСК АВТОМАТИЗАЦИИ Хэш: {commit_sha})", flush=True)
        try:
            subprocess.run(["./deploy.sh", branch, commit_sha], cwd=PROJECT_DIR, check=True)
            print("Деплой успешно завершен!", flush=True)
        except subprocess.CalledProcessError as e:
            print("ОШИБКА!", flush=True)
            
if __name__ == '__main__':
    print(f"Webhook Server запущен на порту {PORT}")
    print(f"Webhook URL: http://webhook.volyanyuk.course.prafdin.ru")
    print(f"URL:   http://app.volyanyuk.course.prafdin.ru")
    print("Ожидаю событий от GitHub...\n")
    HTTPServer(('0.0.0.0', PORT), WebhookHandler).serve_forever()
