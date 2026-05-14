import http.server
import json
import subprocess

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                commit_sha = payload.get('after')
                # Берем хэш прямо из запроса бота и пишем в файл
                if commit_sha and commit_sha != '0000000000000000000000000000000000000000':
                    with open('/home/enjoyer/my-app/.env', 'w') as f:
                        f.write(f'DEPLOY_REF={commit_sha}\n')
            except Exception:
                pass
                
        subprocess.Popen(["/home/enjoyer/deploy.sh"])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deploy started")

if __name__ == "__main__":
    server = http.server.HTTPServer(('0.0.0.0', 8080), WebhookHandler)
    server.serve_forever()
