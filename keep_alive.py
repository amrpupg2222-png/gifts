from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Flask Error: {e}")

def keep_alive():
    # Only start if not already running to avoid port issues
    if not any(t.name == "KeepAlive" for t in threading.enumerate()):
        t = threading.Thread(target=run, name="KeepAlive")
        t.daemon = True
        t.start()
