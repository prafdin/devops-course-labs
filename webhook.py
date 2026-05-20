import http.server
import socketserver
import subprocess
import os

PORT = 8080
REPO_DIR = "/home/rave/catty-reminders-app"

class WebhookHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Быстро отвечаем GitHub, что приняли вебхук
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Deployment triggered!")

        print("\n==================================================")
        print("[WEBHOOK] Received push event from GitHub. Starting deployment...")

        try:
            # 1. Скачиваем новый код из GitHub
            print("[DEPLOY] 1. Pulling latest code from Git...")
            pull_output = subprocess.run(
                ["git", "pull", "origin", "lab1"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True
            )
            print(pull_output.stdout)
            if pull_output.stderr:
                print(f"[GIT WARNING/ERROR]: {pull_output.stderr}")

            # 1.5. Получаем актуальный хеш коммита из Git
            sha_output = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True
            )
            sha = sha_output.stdout.strip()
            print(f"[DEPLOY] Current commit SHA: {sha}")

            # Записываем хеш в файл .env
            env_file_path = os.path.join(REPO_DIR, ".env")
            with open(env_file_path, "w") as f:
                f.write(f"DEPLOY_REF={sha}\n")
            print(f"[DEPLOY] Wrote DEPLOY_REF={sha} to .env")

            # 2. Запускаем юнит-тесты
            print("[DEPLOY] 2. Running pytest unit tests...")
            test_output = subprocess.run(
                ["/home/rave/catty-reminders-app/venv/bin/python3", "-m", "pytest", "tests/test_unit.py"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True
            )
            print(test_output.stdout)

            # 3. Перезапускаем сервис приложения (теперь он считает новый .env)
            print("[DEPLOY] 3. Restarting catty.service...")
            subprocess.run(
                ["sudo", "systemctl", "restart", "catty.service"],
                capture_output=True,
                text=True
            )
            print("[DEPLOY] SUCCESS! Application restarted with new DEPLOY_REF.")
            print("==================================================\n")

        except Exception as e:
            print(f"[ERROR] Deployment failed: {e}")

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), WebhookHandler) as httpd:
    print(f"Webhook server listening on port {PORT}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping webhook server.")

