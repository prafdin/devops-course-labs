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
            ref = payload.get('ref', '')
            branch = ref.split('/')[-1] if ref else "lab1"
            if not ref and 'pull_request' in payload:
                branch = payload['pull_request']['head']['ref']

            full_sha = payload.get('after')
            if not full_sha or full_sha.startswith('000000'):
                if 'head_commit' in payload and payload['head_commit']:
                    full_sha = payload['head_commit'].get('id')
                elif 'pull_request' in payload:
                    full_sha = payload['pull_request']['head'].get('sha')

            project_dir = "/home/kali/catty-reminders-app"
            venv_python = os.path.join(project_dir, "venv/bin/python")

            print(f"\n--- [WEBHOOK] Branch: {branch} | SHA: {full_sha} ---")

            subprocess.run(f"rm -rf {project_dir}/app/__pycache__", shell=True)
            subprocess.run(["git", "-C", project_dir, "fetch", "origin"], check=True)
            subprocess.run(["git", "-C", project_dir, "checkout", "-f", branch], check=True)
            subprocess.run(["git", "-C", project_dir, "reset", "--hard", f"origin/{branch}"], check=True)

            subprocess.run("pkill -9 -f uvicorn || true", shell=True)
            subprocess.run("fuser -k -9 8181/tcp || true", shell=True)
            
            time.sleep(2)
            while is_port_in_use(8181):
                time.sleep(1)

            env = os.environ.copy()
            if full_sha:
                env["DEPLOY_REF"] = str(full_sha)
                print(f"Injecting DEPLOY_REF: {full_sha}")

            cmd = [venv_python, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
            subprocess.Popen(cmd, cwd=project_dir, start_new_session=True, env=env)
            
            print(f"--- [SUCCESS] Deployed SHA: {full_sha} ---")
            
        except Exception as e:
            print(f"--- [ERROR] {e} ---")

print("Deploy Handler v5.0 (THE EXTERMINATOR) listening on port 8080...")
HTTPServer(('0.0.0.0', 8080), DeployHandler).serve_forever()
