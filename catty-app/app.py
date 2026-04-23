from flask import Flask
import datetime

app = Flask(__name__)

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

@app.route('/health')
def health():
    return "OK 200", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181)
