import http.server
import subprocess
import json
import os

APP_DIR = "/home/enjoyer/my-app"
ENV_FILE = "/home/enjoyer/my-app/.env"

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body.decode('utf-8'))
            
            if self.headers.get('X-GitHub-Event') != 'push':
                self.send_response(200)
                self.end_headers()
                return
                
            commit_sha = payload.get('after', '')
            if not commit_sha:
                self.send_response(400)
                self.end_headers()
                return

            print(f"🚀 Начинаем деплой коммита: {commit_sha}")
            
            with open(ENV_FILE, 'w') as f:
                f.write(f"DEPLOY_REF={commit_sha}\n")
            

            subprocess.run(["git", "-C", APP_DIR, "fetch", "origin"], check=True)
            subprocess.run(["git", "-C", APP_DIR, "reset", "--hard", commit_sha], check=True)

            pip_path = os.path.join(APP_DIR, "venv/bin/pip")
            req_path = os.path.join(APP_DIR, "requirements.txt")
            subprocess.run([pip_path, "install", "-r", req_path], check=True)
            
            subprocess.run(["sudo", "systemctl", "restart", "catty-app"], check=True)
            
            print("✅ Деплой успешно завершен")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Success")
            
        except Exception as e:
            print(f"❌ Ошибка деплоя: {e}")
            self.send_response(500)
            self.end_headers()

if __name__ == "__main__":
    server = http.server.HTTPServer(('0.0.0.0', 8080), WebhookHandler)
    print("Webhook handler started on port 8080...")
    server.serve_forever()
