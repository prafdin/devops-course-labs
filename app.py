
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8181

def get_deploy_ref():
    try:
        with open("deployref.txt", "r") as f:
            return f.read().strip()
    except:
        return "unknown"


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        deployref = get_deploy_ref()

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = f"""
        <html>
        <head>
            <title>DevOps Lab</title>
        </head>
        <body>
            <h1>DevOps webhook deployment works</h1>
            <p>deployref={deployref}</p>
        </body>
        </html>
        """

        self.wfile.write(html.encode())


server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"App started on port {PORT}")

server.serve_forever()
