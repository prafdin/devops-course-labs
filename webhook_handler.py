from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def handle_webhook(path):
    data = request.get_json(silent=True) or {}
    
    ref = data.get('ref', 'refs/heads/lab1')
    branch = ref.replace('refs/heads/', '')
    
    print(f"Deploying branch: {branch}")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy.sh")
    subprocess.Popen(["bash", script_path, branch])
    
    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)