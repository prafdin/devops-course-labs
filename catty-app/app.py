from flask import Flask, jsonify, request, make_response
import datetime
import uuid

app = Flask(__name__)

# Простое хранилище сессий (в реальности используйте БД)
sessions = {}

@app.route('/')
def hello():
    return f"""
    <html>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>🐱 Catty Reminders App</h1>
            <p>Successfully deployed via GitHub Webhook!</p>
            <p>Time: {datetime.datetime.now()}</p>
            <hr>
            <small>DevOps Lab - Webhook Automation</small>
        </body>
    </html>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Создаем сессию
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"user": "test_user", "logged_in": True}
        
        # Создаем ответ с cookie
        resp = make_response(jsonify({"success": True, "message": "Login successful"}))
        resp.set_cookie('session_id', session_id, httponly=True, max_age=3600)
        return resp
    
    # GET запрос - возвращаем форму логина
    return """
    <html>
        <body>
            <h1>Login</h1>
            <form method="post">
                <input type="text" name="username" placeholder="Username">
                <input type="password" name="password" placeholder="Password">
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    """

@app.route('/logout', methods=['POST'])
def logout():
    session_id = request.cookies.get('session_id')
    if session_id in sessions:
        del sessions[session_id]
    resp = make_response(jsonify({"success": True}))
    resp.set_cookie('session_id', '', expires=0)
    return resp

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181)
