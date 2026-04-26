import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_webhook():
    data = request.json
    if data and 'ref' in data:
        branch = data['ref'].split('/')[-1]
        print(f"Received push to the branch. Launching deploy...")
        subprocess.Popen(['/bin/bash', '/home/nightainted/catty-reminders-app/deploy.sh', branch])
        return "Deployment started", 200
    return "Not a push event", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
