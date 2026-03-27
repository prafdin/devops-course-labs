from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>Hello! App is running and updating via Webhooks!</h1>")

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8181), Handler)
    print("App started on port 8181...")
    server.serve_forever()
