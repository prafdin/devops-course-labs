import subprocess
import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

APP_PATH = "/home/dima/devops/catty-reminders-app"
SERVICE_NAME = "catty-app"

@app.route('/', methods=['POST'])
def webhook():
    event_type = request.headers.get('X-GitHub-Event', '')
    
    if event_type != 'push':
        print(f"Ignored event: {event_type}")
        return jsonify({"message": "Ignored"}), 200
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data"}), 400
    
    sha = data.get('after')
    if not sha or sha == '0000000000000000000000000000000000000000':
        return jsonify({"error": "No valid SHA"}), 400
    
    ref = data.get('ref', '')
    branch = ref.split('/')[-1] if ref else 'catty-reminders-app'
    
    print(f"=== Webhook received ===")
    print(f"Branch: {branch}")
    print(f"SHA: {sha}")
    
    env_file = f"{APP_PATH}/.env"
    with open(env_file, 'w') as f:
        f.write(f"DEPLOY_REF={sha}\n")
    

    commands = f"""
    cd {APP_PATH} && \
    git fetch origin && \
    git checkout {branch} && \
    git reset --hard {sha}
    """
    
    try:
        result = subprocess.run(
            commands,
            shell=True,
            capture_output=True,
            text=True,
            executable='/bin/bash',
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"Git updated to {sha}")
            subprocess.run(f"sudo systemctl restart {SERVICE_NAME}", shell=True)
            print(f"Service restarted")
            return jsonify({"status": "success", "sha": sha}), 200
        else:
            print(f"Error: {result.stderr}")
            return jsonify({"status": "error", "error": result.stderr}), 500
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "alive"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
