from flask import Flask
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return "App is running!", 200

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8181
    app.run(host='0.0.0.0', port=port)
