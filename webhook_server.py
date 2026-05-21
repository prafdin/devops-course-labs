from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class GitHubWebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        event = self.headers.get("X-GitHub-Event", "unknown")
        delivery = self.headers.get("X-GitHub-Delivery", "unknown")

        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid json"}).encode("utf-8"))
            return

        print(f"GitHub event: {event}")
        print(f"Delivery ID: {delivery}")
        print("Payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8080

    server = HTTPServer((host, port), GitHubWebhookHandler)
    print(f"Server started on http://{host}:{port}")
    server.serve_forever()
