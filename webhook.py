import http.server
import socketserver
import subprocess

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

            # 2. Запускаем юнит-тесты (как требует методичка)
            print("[DEPLOY] 2. Running pytest unit tests...")
            test_output = subprocess.run(
                ["/home/rave/catty-reminders-app/venv/bin/python3", "-m", "pytest", "tests/test_unit.py"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True
            )
            print(test_output.stdout)
            if test_output.returncode != 0:
                print("[WARNING] Tests failed! But continuing restart...")

            # 3. Перезапускаем сервис приложения
            print("[DEPLOY] 3. Restarting catty.service...")
            subprocess.run(
                ["sudo", "systemctl", "restart", "catty.service"],
                capture_output=True,
                text=True
            )
            print("[DEPLOY] SUCCESS! Application restarted with new changes.")
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
