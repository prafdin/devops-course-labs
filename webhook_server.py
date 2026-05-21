from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import threading
import logging

REPO_DIR = "/home/vboxuser/catty-reminders-app"
ENV_FILE = "/etc/catty.env"
SERVICE = "catty"
HOST = "0.0.0.0"
PORT = 8080

logging.basicConfig(
    filename="/home/vboxuser/deploy.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


def deploy(sha):
    try:
        subprocess.run(["git", "-C", REPO_DIR, "fetch", "--all"], check=True)
        subprocess.run(["git", "-C", REPO_DIR, "reset", "--hard", sha], check=True)

        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"DEPLOY_REF={sha}\n")

        subprocess.run(["sudo", "systemctl", "restart", SERVICE], check=True)
        logging.info("Deployed %s", sha)

    except Exception as e:
        logging.error("Deploy error: %s", e)


class GitHubWebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        event = self.headers.get("X-GitHub-Event", "")

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid json"}).encode("utf-8"))
            return

        if event == "push":
            sha = payload.get("after")
            if sha and sha != "0000000000000000000000000000000000000000":
                thread = threading.Thread(target=deploy, args=(sha,))
                thread.daemon = True
                thread.start()

                self.send_response(202)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"Deploy started")
                return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Ignored")

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), GitHubWebhookHandler)
    print(f"Server started on http://{HOST}:{PORT}")
    server.serve_forever()
