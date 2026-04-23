#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json
import subprocess
import os
import urllib.parse

PORT = 8181

class AppHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Получаем последний коммит
            commit_hash = "unknown"
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=os.path.dirname(__file__),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    commit_hash = result.stdout.strip()
            except:
                pass
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>DevOps App</title></head>
            <body>
                <h1>DevOps App</h1>
                <p>Time: {datetime.now()}</p>
                <p>Commit: {commit_hash}</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "Login successful"}).encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/login':
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Парсим данные формы или JSON
            try:
                if 'application/json' in self.headers.get('Content-Type', ''):
                    data = json.loads(post_data.decode('utf-8'))
                else:
                    data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                
                # Простая валидация (можно любые логин/пароль для тестов)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "message": "Login successful"}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
        
        elif self.path == '/webhook':
            # Обработка webhook от GitHub
            try:
                # Pull последних изменений
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=os.path.dirname(__file__),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Перезапуск сервиса (ОБЯЗАТЕЛЬНО для обновления commit hash!)
                subprocess.Popen(
                    ["sudo", "systemctl", "restart", "devops-app"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "ok", 
                    "message": "Webhook received",
                    "output": result.stdout
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Уменьшаем шум в логах
        print(f"{datetime.now()} - {format % args}")

def main():
    print(f"Server starting on port {PORT}")
    print(f"Access at: http://localhost:{PORT}")
    server = HTTPServer(('0.0.0.0', PORT), AppHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.server_close()

if __name__ == '__main__':
    main()
