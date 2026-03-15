from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import os

PORT = 8080

class WebhookHandler(BaseHTTPRequestHandler):

	def do_POST(self):
		content_length = int(self.headers.get('Content-Length', 0))
		body = self.rfile.read(content_length)

		try:
			payload = json.loads(body.decode('utf-8'))
		except json.JSONDecodeError:
			print("Ошибка парсинга JSON")
			self.send_response(400)
			self.end_headers()
			return

		event = self.headers.get("X-GitHub-Event")

		if event == "ping":
			print("Получен ping от Github")
			self.send_response(200)
			self.end_headers()
			self.wfile.write(b"pong")
			return
		
		branch = payload.get('ref', '').replace('refs/heads/', '')
		print(f"Событие: {event}, ветка: {branch}")
		
		if event == "push":
			print(f"Запускается деплой для ветки {branch}")
			subprocess.run(["/home/mappy/Desktop/catty-reminders-app/webhook/deploy.sh", branch])

		self.send_response(200)
		self.end_headers()
		self.wfile.write(b"ok")
	
	def do_GET(self):
		self.send_response(200)
		self.end_headers()
		self.wfile.write(b"Hello! I'm a webhook server. Use POST to trigger deployment.\n")

server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
print(f"Вебхук запущен на порту {PORT}")
server.serve_forever()
