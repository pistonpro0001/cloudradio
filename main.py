from flask import Flask
import threading
import scratchattach as sa
import time
import random
import os

app = Flask(__name__)

status = ['<span style="color:gold">Booting...</span>']
@app.route('/')
def home():
    return '<pre style="font-size:22px">' + "\n".join(status[-150:]) + "</pre>"

def log(msg, color="grey"):
    global status
    status.append(f'<span style="color:{color}">{msg}</span>')

def run_bot():
    global status
    try_ = 0
    while True:
        if try_ != 0:
            log("Reconnecting...", "gold")
        try:
            session = sa.login(os.getenv("SCRATCH_USER"), os.getenv("SCRATCH_PASS"))
            cloud = session.connect_cloud("1314420436")
            log("Cloud is ready", "lime")
            while True:
                log("Starting new phase...")
                cloud.set_var("ready?", "0")
                total_time = float(cloud.get_var("track-length")) #no need to check if it isdigit, will always be a number to two decimals
                log(f"Song length is {total_time} secs")
                log("Sleeping the song out.")
                start = time.time()
                while True:
                    elapsed = time.time() - start
                    cloud.set_var("progress", round(elapsed, 1))
                    if elapsed >= total_time:
                        break
                    time.sleep(.1)
                cloud.set_var("song-#", str(random.randint(1, 2)))
                cloud.set_var("ready?", "1")
                log("Successfully restarted and chose new song!")
                time.sleep(2)
        except Exception as e:
            import traceback
            traceback.print_exc()
            try_ += 1
            log(f'Errored: "{e}", try #{try_}', "red")
            time.sleep(3)

threading.Thread(target=run_bot, daemon=True).start()

app.run(host="0.0.0.0", port=10000)