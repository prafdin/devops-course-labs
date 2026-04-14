import subprocess
from flask import Flask, request

app = Flask(__name__)

APP_PATH = "/home/dima/devops/catty-reminders-app"
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
    
    try:
        # 1. Fetch и reset
        subprocess.run(f"cd {APP_PATH} && git fetch origin", shell=True, capture_output=True, text=True, check=False)
        subprocess.run(f"cd {APP_PATH} && git reset --hard {sha}", shell=True, capture_output=True, text=True, check=False)
        
        # 2. ЗАПИСЬ SHA В .env (самое важное!)
        result = subprocess.run(f"echo 'DEPLOY_REF={sha}' > {APP_PATH}/.env", shell=True, capture_output=True, text=True)
        print(f"Writing .env: {result.stdout} {result.stderr}")
        
        # 3. Перезапуск сервиса
        subprocess.run(f"sudo /usr/bin/systemctl restart {SERVICE_NAME}", shell=True, capture_output=True, text=True)
        
        print(f"SUCCESS: Deployed {sha}")
        return f"OK: Deployed {sha}", 200
        
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
