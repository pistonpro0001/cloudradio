from flask import Flask
import threading
import scratchattach as sa
import time
import random
import os

app = Flask(__name__)

status = ["Cloud is ready"]
@app.route('/')
def home():
    return "\n".join(status[-15:])

def run_bot():
    global status
    try_ = 0
    while True:
        if try_ != 0:
            status.append("Reconnecting...")
        try:
            session = sa.login(os.getenv("SCRATCH_USER"), os.getenv("SCRATCH_PASS"))
            cloud = session.connect_cloud("1314420436")
            status.append("Cloud is ready")
            while True:
                status.append("Starting new phase...")
                cloud.set_var("ready?", "0")
                total_time = float(cloud.get_var("track-length")) #no need to check if it isdigit, will always be a number to two decimals
                status.append(f"Song length is {total_time} secs")
                status.append("Sleeping the song out.")
                start = time.time()
                while True:
                    elapsed = time.time() - start
                    cloud.set_var("progress", round(elapsed, 1))
                    if elapsed >= total_time:
                        break
                    time.sleep(.1)
                cloud.set_var("song-#", str(random.randint(1, 2)))
                cloud.set_var("ready?", "1")
                status.append("Successfully restarted and chose new song!")
                time.sleep(2)
        except Exception as e:
            import traceback
            traceback.print_exc()
            try_ += 1
            status.append(f"Errored: {e}, try #{try_}")
            time.sleep(3)

threading.Thread(target=run_bot, daemon=True).start()

app.run(host="0.0.0.0", port=10000)