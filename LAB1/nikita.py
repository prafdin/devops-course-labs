import subprocess
from flask import Flask, request

app = Flask(__name__)

APP_PATH = "/home/vboxuser/Desktop/devops/catty-reminders-app"
SERVICE_NAME = "catty-app"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return 'No JSON data', 400

    sha = data.get('after')
    if not sha or sha == "0000000000000000000000000000000000000000":
        return 'No commit SHA found', 400
    
    print(f">>> Received webhook for SHA: {sha}")

    cmds = [
        f"cd {APP_PATH}",
        "git fetch origin",
        f"git reset --hard {sha}",  
        f"echo 'DEPLOY_REF={sha}' > {APP_PATH}/.env", 
        f"sudo /usr/bin/systemctl restart {SERVICE_NAME}"  
    ]
    
    full_command = " && ".join(cmds)
    
    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"SUCCESS: Deployed {sha}")
            return f"OK: Deployed {sha}", 200
        else:
            print(f"ERROR: {result.stderr}")
            return result.stderr, 500
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
