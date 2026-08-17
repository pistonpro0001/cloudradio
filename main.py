from flask import Flask
import threading
import scratchattach as sa
import time
import random
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "alive"

def run_bot():
    while True:
        try:
            session = sa.login(os.getenv("SCRATCH_USER"), os.getenv("SCRATCH_PASS"))
            cloud = session.connect_cloud("1314420436")
            while True:
                print("Starting new phase...")
                cloud.set_var("ready?", "0")
                total_time = float(cloud.get_var("track-length")) #no need to check if it isdigit, will always be a number to two decimals
                print(f"Song length is {total_time} secs")
                print("Sleeping the song out.")
                time.sleep(total_time)
                cloud.set_var("song-#", str(random.randint(1, 2)))
                cloud.set_var("ready?", "1")
                print("Successfully restarted and chose new song!")
                time.sleep(2)
        except Exception as e:
            import traceback
            traceback.print_exc()
            time.sleep(3)

threading.Thread(target=run_bot, daemon=True).start()

app.run(host="0.0.0.0", port=10000)