from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "alive"

def run_bot():
    print("this estch a test")
    while True:
        pass #placeholder

threading.Thread(target=run_bot).start()

app.run(host="0.0.0.0", port=10000)