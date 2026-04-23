from flask import Flask, jsonify, request, make_response
import datetime
import uuid
import subprocess
import os

app = Flask(__name__)

# Хранилище сессий и напоминаний
sessions = {}
reminders = {"1": {"id": "1", "text": "Сдать DevOps лабу", "completed": False}}

def get_current_commit():
    """Возвращает текущий commit hash (короткий)"""
    try:
        repo_path = os.path.dirname(os.path.abspath(__file__))
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                        cwd=repo_path, 
                                        stderr=subprocess.DEVNULL).decode().strip()
        return commit
    except:
        return "unknown"

@app.route('/')
def hello():
    commit_hash = get_current_commit()
    return f"""
    <html>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>🐱 Catty Reminders App</h1>
            <p>Successfully deployed via GitHub Webhook!</p>
            <p>Commit: {commit_hash}</p>
            <p>Time: {datetime.datetime.now()}</p>
            <hr>
            <small>DevOps Lab - Webhook Automation</small>
        </body>
    </html>
    """

@app.route('/login', methods=['POST'])
def login():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"user": "test_user"}
    
    resp = make_response(jsonify({"success": True, "message": "Login successful"}))
    resp.set_cookie('session_id', session_id, httponly=True, max_age=3600)
    return resp

@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    session_id = request.cookies.get('session_id')
    if not session_id or session_id not in sessions:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(list(reminders.values()))

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181)
