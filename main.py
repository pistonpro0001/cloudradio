from flask import Flask
import threading
import scratchattach as sa
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

# --- SCRATCHATTACH BUG #608 ---
original_process = sa.Session._process_session_id

def patched_process_session_id(self):
    try:
        original_process(self)
    except KeyError as e:
        if str(e) == "'_language'":
            self.language = "en"
            print("[Patch] Bypassed missing '_language' key successfully.")
        else:
            raise e

sa.Session._process_session_id = patched_process_session_id

app = Flask(__name__)

status = ['<span style="color:gold">Booting...</span>']
@app.route('/')
def home():
    return '<pre style="font-size:22px">' + "\n".join(status[-150:]) + "</pre>"

def log(msg, color="grey"):
    global status
    status.append(f'<span style="color:{color}">{msg}</span>')
    print(msg)

track_lengths = [147.53, 354.02, 175.2, 162.04, 183.44, 193.37, 185.56, 235.55, 261.75, 189.86, 151.35, 208.08]
print(os.getenv("SCRATCH_USER"))
def run_bot():
    global status
    try_ = 0
    while True:
        if try_ != 0:
            log("Reconnecting...", "gold")
        try:
            session = sa.login_by_id(os.getenv("SC_SESS_ID"))
            cloud = session.connect_cloud("1314420436")
            log("Cloud is ready", "lime")
            
            while True:
                log("Starting new phase...")
                cloud.set_var("ready?", "0")
                cur_song = cloud.get_var("song-#")
                if cur_song is None:
                    cur_song = random.randint(0, len(track_lengths)-1)
                    log("Could not get the song number, resetting it to a random number.", "red")
                    cloud.set_var("song-#", str(cur_song+1))
                total_time = track_lengths[int(cur_song)] * 100
                cloud.set_var("tracklength", str(total_time))
                total_time /= 100
                log(f"Song length is {total_time} secs")
                log("Sleeping the song out.")
                start = time.time()
                
                while True:
                    elapsed = time.time() - start
                    cloud.set_var("progress", round(elapsed, 1))
                    if elapsed >= total_time:
                        break
                    time.sleep(.1)
                cloud.set_var("song-#", str(random.randint(1, len(track_lengths))))
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

app.run(host="0.0.0.0", port=11303, debug=True)