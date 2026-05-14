from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import os
import time
import json

class DeployHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deployment started")

        try:
            payload = json.loads(post_data.decode('utf-8'))
            ref = payload.get('ref', 'refs/heads/lab1')
            branch = ref.split('/')[-1]
            print(f"\n--- [Webhook Received] Branch: {branch} ---")
            
            project_dir = os.path.expanduser("~/catty-reminders-app")
            venv_python = os.path.join(project_dir, "venv/bin/python")

            print(f"Force updating to origin/{branch}...")
            subprocess.run(["git", "-C", project_dir, "fetch", "origin"], check=True)
            # Переключаемся на ветку, которую прислал бот
            subprocess.run(["git", "-C", project_dir, "checkout", branch], check=True)
            subprocess.run(["git", "-C", project_dir, "reset", "--hard", f"origin/{branch}"], check=True)

            print("Force clearing port 8181...")
            subprocess.run("sudo fuser -k 8181/tcp || true", shell=True)
            time.sleep(2)

            print("Starting application on port 8181...")
            cmd = [venv_python, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8181"]
            subprocess.Popen(cmd, cwd=project_dir, start_new_session=True)
            
            print(f"--- [Success] Updated to branch {branch} ---")
        except Exception as e:
            print(f"--- [Error] Deployment failed: {e} ---")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

print("Smart Webhook handler is listening on port 8080...")
HTTPServer(('0.0.0.0', 8080), DeployHandler).serve_forever()
