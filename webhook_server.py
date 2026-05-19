from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import threading

HOST = "0.0.0.0"
PORT = 8080

def run_deploy():
    subprocess.run(["bash", "/home/vboxuser/catty-reminders-app/deploy.sh"])

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self):
        event = self.headers.get("X-GitHub-Event", "")
        length = int(self.headers.get("Content-Length", 0))
        _body = self.rfile.read(length)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

        if event == "push":
            threading.Thread(target=run_deploy, daemon=True).start()

HTTPServer((HOST, PORT), Handler).serve_forever()
