from flask import Flask, request, jsonify
import subprocess
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

REPO_PATH = "/home/vano/catty-app"
VENV_PIP = "/home/vano/catty-reminders-app/venv/bin/pip"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"status": "no data"}), 400
    
    if "ref" in data and data.get("ref") == "refs/heads/main":
        logging.info("Push event received on main branch")
        
        logging.info("Pulling latest code...")
        subprocess.run(["git", "-C", REPO_PATH, "pull"], check=False)
        
        logging.info("Installing dependencies...")
        subprocess.run([VENV_PIP, "install", "-r", f"{REPO_PATH}/requirements.txt"], check=False)
        
        logging.info("Restarting catty service...")
        subprocess.run(["sudo", "systemctl", "restart", "catty"], check=False)
        
        return jsonify({"status": "deploy started"}), 200
    
    return jsonify({"status": "ignored"}), 200

@app.route("/", methods=["GET"])
def index():
    return "Webhook handler is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
