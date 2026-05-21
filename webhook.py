import http.server
import socketserver
import subprocess
import os
import json

PORT = 8080
REPO_DIR = "/home/rave/catty-reminders-app"

class WebhookHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Быстро отвечаем GitHub, что приняли вебхук
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Deployment triggered!")

        # Читаем тело JSON-запроса от GitHub
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b""
        
        try:
            payload = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception as e:
            payload = {}
            print(f"[WEBHOOK] Error parsing JSON payload: {e}")

        # Игнорируем пинг-события от GitHub
        if "zen" in payload or payload.get("hook_id"):
            print("[WEBHOOK] Received GitHub ping event. Ignored.")
            return

        print("\n==================================================")
        print("[WEBHOOK] Received push event from GitHub. Starting deployment...")

        # Извлекаем данные из вебхука
        ref = payload.get("ref", "")
        if ref.startswith("refs/heads/"):
            branch = ref[len("refs/heads/"):]
        else:
            branch = "lab1"

        sha = payload.get("after", "")
        # Если это событие pull_request, SHA лежит в другом месте
        if not sha and "pull_request" in payload:
            sha = payload["pull_request"]["head"]["sha"]

        repo_url = payload.get("repository", {}).get("clone_url")
        if not repo_url:
            repo_url = "https://github.com/zurmes/catty-reminders-app.git"

        print(f"[DEPLOY] Target Repository: {repo_url}")
        print(f"[DEPLOY] Target Branch: {branch}")
        print(f"[DEPLOY] Target SHA: {sha if sha else 'Latest HEAD'}")

        try:
            # Настройка неинтерактивного Git (чтобы не зависало на паролях)
            os.environ["GIT_TERMINAL_PROMPT"] = "0"

            # 1. Скачиваем изменения из репозитория, указанного в вебхуке
            print(f"[DEPLOY] 1. Fetching from {repo_url}...")
            subprocess.run(
                ["git", "fetch", "--prune", repo_url, "+refs/heads/*:refs/remotes/origin/*"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True,
                check=True
            )

            # Переключаемся на нужную ветку
            print(f"[DEPLOY] Checking out branch {branch}...")
            subprocess.run(
                ["git", "checkout", "-B", branch, f"origin/{branch}"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True,
                check=True
            )

            # Если передан конкретный коммит, сбрасываем состояние до него
            if sha and not all(c == '0' for c in sha):
                print(f"[DEPLOY] Resetting hard to target SHA: {sha}")
                reset_res = subprocess.run(
                    ["git", "reset", "--hard", sha],
                    cwd=REPO_DIR,
                    capture_output=True,
                    text=True
                )
                if reset_res.returncode != 0:
                    # Если коммит не найден в обычном fetch, пробуем скачать его напрямую
                    print("[DEPLOY] SHA not found in standard fetch. Trying direct fetch...")
                    subprocess.run(
                        ["git", "fetch", repo_url, sha],
                        cwd=REPO_DIR,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    subprocess.run(
                        ["git", "reset", "--hard", sha],
                        cwd=REPO_DIR,
                        capture_output=True,
                        text=True,
                        check=True
                    )
            else:
                print(f"[DEPLOY] No specific SHA. Resetting to origin/{branch}")
                subprocess.run(
                    ["git", "reset", "--hard", f"origin/{branch}"],
                    cwd=REPO_DIR,
                    capture_output=True,
                    text=True,
                    check=True
                )

            # Получаем итоговый хеш коммита на виртуалке
            sha_output = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True,
                check=True
            )
            deployed_sha = sha_output.stdout.strip()
            print(f"[DEPLOY] Deployed SHA on VM: {deployed_sha}")

            # Записываем его в файл .env
            env_file_path = os.path.join(REPO_DIR, ".env")
            with open(env_file_path, "w") as f:
                f.write(f"DEPLOY_REF={deployed_sha}\n")
            print(f"[DEPLOY] Wrote DEPLOY_REF={deployed_sha} to .env")

            # 2. Запускаем тесты
            print("[DEPLOY] 2. Running pytest unit tests...")
            test_output = subprocess.run(
                ["/home/rave/catty-reminders-app/venv/bin/python3", "-m", "pytest", "tests/test_unit.py"],
                cwd=REPO_DIR,
                capture_output=True,
                text=True
            )
            print(test_output.stdout)

            # 3. Перезапускаем службу приложения
            print("[DEPLOY] 3. Restarting catty.service...")
            subprocess.run(
                ["sudo", "systemctl", "restart", "catty.service"],
                capture_output=True,
                text=True,
                check=True
            )
            print("[DEPLOY] SUCCESS! Application restarted with target DEPLOY_REF.")
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
