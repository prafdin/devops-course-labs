from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import threading
import json

HOST = "0.0.0.0"
PORT = 8080


def run_deploy(ref: str, commit_sha: str):
    subprocess.run(
        ["bash", "/home/vboxuser/catty-reminders-app/deploy.sh", ref, commit_sha]
    )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self):
        event = self.headers.get("X-GitHub-Event", "")
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

        if event != "push":
            return

        try:
            payload = json.loads(body.decode("utf-8"))
            ref = payload.get("ref", "")
            commit_sha = payload.get("after", "")
        except Exception:
            return

        if ref and commit_sha:
            threading.Thread(
                target=run_deploy,
                args=(ref, commit_sha),
                daemon=True
            ).start()


HTTPServer((HOST, PORT), Handler).serve_forever()
