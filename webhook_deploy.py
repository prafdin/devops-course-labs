import subprocess
import os
import time
import json
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

class DeployHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

        try:
            payload = json.loads(post_data.decode('utf-8'))
            
            # 1. Глубокий поиск SHA коммита
            full_sha = payload.get('after')
            if not full_sha or full_sha.startswith('000000'):
                if 'head_commit' in payload and payload['head_commit']:
                    full_sha = payload['head_commit'].get('id')
                elif 'pull_request' in payload:
                    full_sha = payload['pull_request']['head'].get('sha')
            
            # Извлекаем ветку (по умолчанию lab1, если пушится в неё)
            branch = payload.get('ref', 'refs/heads/lab1').split('/')[-1]

            project_dir = "/home/kali/catty-reminders-app"
            venv_python = os.path.join(project_dir, ".venv/bin/python")

            print(f"\n--- [WEBHOOK] SHA: {full_sha} ---")

            # 2. Обновление кода
            subprocess.run(["git", "-C", project_dir, "fetch", "origin"], check=True)
            subprocess.run(["git", "-C", project_dir, "checkout", "-f", branch], check=True)
            subprocess.run(["git", "-C", project_dir, "reset", "--hard", f"origin/{branch}"], check=True)

            # 3. Жесткая зачистка портов
            subprocess.run("fuser -k -9 8181/tcp || true", shell=True)
            subprocess.run("pkill -9 -f uvicorn || true", shell=True)
            time.sleep(3) # Даем системе время освободить сокет

            # 4. Запуск с ЯВНЫМ указанием переменной (Shell Injection Mode)
            deploy_cmd = f"DEPLOY_REF={full_sha} {venv_python} -m uvicorn app.main:app --host 0.0.0.0 --port 8181"
            
            subprocess.Popen(deploy_cmd, cwd=project_dir, shell=True, start_new_session=True)
            
            print(f"--- [SUCCESS] Started with DEPLOY_REF={full_sha} ---")
            
        except Exception as e:
            print(f"--- [ERROR] {e} ---")

print("Deploy Handler listening on port 8080...")
HTTPServer(('0.0.0.0', 8080), DeployHandler).serve_forever()
