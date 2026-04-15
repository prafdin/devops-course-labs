import logging
import subprocess
import threading

from flask import Flask, jsonify, request

REPO_DIR = "/home/semen/catty-reminders-app"
ENV_FILE = "/home/semen/catty-app-env"
SERVICE_NAME = "catty-app"

app = Flask(__name__)

logging.basicConfig(
    filename="/home/semen/webhook-handler/webhook.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def run_deploy(sha: str):
    try:
        subprocess.run(["git", "-C", REPO_DIR, "fetch", "--all"], check=True)
        subprocess.run(["git", "-C", REPO_DIR, "reset", "--hard", sha], check=True)
        subprocess.run(
            [f"{REPO_DIR}/venv/bin/pip", "install", "-r", f"{REPO_DIR}/requirements.txt"],
            check=True,
        )

        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={sha}\n")

        subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME], check=True)
        logging.info("deploy success: %s", sha)
    except Exception as e:
        logging.exception("deploy failed for %s: %s", sha, e)

@app.route("/", methods=["GET"])
def health():
    return "ok", 200

@app.route("/", methods=["POST"])
def handle():
    if request.headers.get("X-GitHub-Event") != "push":
        return jsonify({"status": "ignored"}), 200

    payload = request.get_json(silent=True) or {}
    sha = payload.get("after")

    if not sha or sha == "0000000000000000000000000000000000000000":
        return jsonify({"status": "ignored"}), 200

    threading.Thread(target=run_deploy, args=(sha,), daemon=True).start()
    return jsonify({"status": "accepted", "sha": sha}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
