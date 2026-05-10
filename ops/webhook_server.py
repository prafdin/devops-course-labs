#!/usr/bin/env python3
import hashlib
import hmac
import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


DEPLOY_SCRIPT = os.getenv("DEPLOY_SCRIPT", "/opt/catty-reminders-app/current/ops/deploy.sh")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
MAX_BODY_SIZE = 1024 * 1024


def _valid_signature(body: bytes, signature: str) -> bool:
  if not WEBHOOK_SECRET:
    return True
  if not signature.startswith("sha256="):
    return False

  digest = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
  return hmac.compare_digest(signature, f"sha256={digest}")


class WebhookHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path == "/health":
      self._write(200, b"ok\n")
    else:
      self._write(404, b"not found\n")

  def do_POST(self):
    body = self._read_body()
    if body is None:
      self._write(413, b"payload too large\n")
      return

    signature = self.headers.get("X-Hub-Signature-256", "")
    if not _valid_signature(body, signature):
      self._write(401, b"invalid signature\n")
      return

    event = self.headers.get("X-GitHub-Event", "")
    if event == "ping":
      self._write(200, b"pong\n")
      return
    if event != "push":
      self._write(202, b"ignored\n")
      return

    try:
      payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
      self._write(400, b"invalid json\n")
      return

    commit_sha = payload.get("after", "")
    ref = payload.get("ref", "")
    branch = ref.removeprefix("refs/heads/")

    if not commit_sha or set(commit_sha) == {"0"} or not branch:
      self._write(202, b"ignored\n")
      return

    subprocess.Popen([DEPLOY_SCRIPT, commit_sha, branch])
    self._write(202, b"deploy started\n")

  def _read_body(self):
    length = int(self.headers.get("Content-Length", "0"))
    if length > MAX_BODY_SIZE:
      return None
    return self.rfile.read(length)

  def _write(self, status: int, body: bytes):
    self.send_response(status)
    self.send_header("Content-Type", "text/plain; charset=utf-8")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)


if __name__ == "__main__":
  server = ThreadingHTTPServer((WEBHOOK_HOST, WEBHOOK_PORT), WebhookHandler)
  print(f"Webhook server listening on {WEBHOOK_HOST}:{WEBHOOK_PORT}", flush=True)
  server.serve_forever()
