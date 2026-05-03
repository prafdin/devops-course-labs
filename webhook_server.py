from flask import Flask, request
from flask import jsonify
import subprocess
import os

app = Flask(__name__)

PORT = 8080
APP_DIR = "/home/user/catty-reminders-app"
APP_SERVICE = "catty-app"
ENV_FILE = "/home/user/catty-reminders-app/.env"

@app.route('/', methods=['GET', 'POST'])
def handle():
    if request.method == 'GET':
        return jsonify({"message": "Webhook handler running"}), 200
    
    if request.headers.get('X-GitHub-Event') == 'push':
        data = request.json
        commit_sha = data.get('after') if data else None
        
        if not commit_sha or commit_sha == '0000000000000000000000000000000000000000':
            return jsonify({"message": "No valid SHA"}), 200
            
        print("Starting deployment...")
        
        subprocess.run(["git", "-C", APP_DIR, "pull"], check=True)
        print("Code updated")
        
        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={commit_sha}")
        print(f"DEPLOY_REF written: {commit_sha}")
        
        subprocess.run(["sudo", "systemctl", "restart", APP_SERVICE], check=True)
        print("Service restarted")
        
        return jsonify({"message": "Deployment completed"}), 200
        
    return jsonify({"message": "Not a push event"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
