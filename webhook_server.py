import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

def run_deploy(commit_sha):
    print(f"=== Starting background deployment for SHA: {commit_sha} ===")
    try:
        # Передаем commit_sha аргументом в deploy.sh, если он есть
        args = ["/home/alexander/deploy.sh"]
        if commit_sha:
            args.append(commit_sha)
            
        process = subprocess.run(args, capture_output=True, text=True)
        print("Deploy Script Output:\n", process.stdout)
        print("Deploy Script Error:\n", process.stderr)
        print("=== Background deployment finished ===")
    except Exception as e:
        print("Error executing deploy.sh in background:", str(e))

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("=== Webhook received! ===")
        commit_sha = None
        try:
            # Читаем и парсим JSON-тело входящего вебхука
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            
            # Достаем хэш коммита из стандартных полей GitHub Webhook
            commit_sha = payload.get('after')
            if not commit_sha and 'head_commit' in payload:
                commit_sha = payload['head_commit'].get('id')
            
            print(f"Successfully parsed commit SHA: {commit_sha}")
        except Exception as e:
            print("Error parsing webhook payload:", str(e))
        
        # Запускаем сборку асинхронно в отдельном потоке и передаем туда хэш
        threading.Thread(target=run_deploy, args=(commit_sha,)).start()
        
        # Мгновенно отвечаем клиенту, чтобы избежать таймаута
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Deployment triggered in background")

    def do_GET(self):
        # Для проверок работоспособности (ping)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"ok")

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), WebhookHandler)
    print("Webhook listener running on port 8080...")
    server.serve_forever()
