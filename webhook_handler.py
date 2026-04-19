from flask import Flask, request, jsonify
import subprocess, logging, os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

REPO_PATH = "/home/vboxuser/catty-reminders-app"
VENV_PIP = REPO_PATH + "/venv/bin/pip"
SERVICE_NAME = "catty"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"status": "no data"}), 400
    event = request.headers.get('X-GitHub-Event')
    ref = data.get('ref', '')
    after = data.get('after', 'unknown')
    logging.info(f"{event} {ref} {after[:7]}")
    if event == "push" and ref.startswith("refs/heads/"):
        branch = ref.split('/')[-1]
        with open(os.path.join(REPO_PATH, "deploy_ref.txt"), 'w') as f:
            f.write(after[:7])
        subprocess.run(["git", "-C", REPO_PATH, "pull", "origin", branch])
        if os.path.exists(os.path.join(REPO_PATH, "requirements.txt")):
            subprocess.run([VENV_PIP, "install", "-r", os.path.join(REPO_PATH, "requirements.txt")])
        subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME])
        return jsonify({"status": "ok", "commit": after[:7]}), 200
    return jsonify({"status": "ignored"}), 200

@app.route("/")
def health():
    return "Webhook handler is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
