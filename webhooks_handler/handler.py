from flask import Flask, request, abort
import subprocess

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    if request.headers.get("X-GitHub-Event") != "push":
        return "Ignored"

    payload = request.json
    ref = payload["ref"]
    branch = ref.split("/")[-1]

    print(f"Push в ветку: {branch}")

    result = subprocess.run(["/srv/deploy.sh", branch])

    if result.returncode != 0:
        abort(500)

    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)