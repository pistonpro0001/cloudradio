from flask import Flask
import threading
import scratchattach as sa
import time
import random
import os
import warnings
warnings.filterwarnings('ignore', category=sa.LoginDataWarning)

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

#sa.Session._process_session_id = patched_process_session_id

app = Flask(__name__)

status = ['<span style="color:gold">Booting...</span>']
@app.route('/')
def home():
    return '<pre style="font-size:22px">' + "\n".join(status[-150:]) + "</pre>"

def log(msg, color="grey"):
    global status
    status.append(f'<span style="color:{color}">{msg}</span>')
    #print(msg)

track_lengths = [147.53, 354.02, 175.2, 162.04, 183.44, 193.37, 185.56, 235.55, 261.75, 189.86, 151.35, 208.08]
print(os.getenv("SCRATCH_USER"))
def run_bot():
    global status
    try_ = 0
    while True:
        if try_ != 0:
            log("Reconnecting...", "gold")
        try:
            try:
                session = sa.login(os.getenv("SCRATCH_USER"), os.getenv("SCRATCH_PASS"))
                log("Managed to login via username and password.", "gold")
            except:
                log("Couldn't login via username and password, using session id", "red")
                session = sa.login_by_id(os.getenv("SC_SESS_ID"))
            
            cloud = session.connect_cloud(project_id="1334822091")
            log("Cloud is ready", "lime")
            
            while True:
                log("Starting new phase...")
                cloud.set_var("ready", "0")
                time.sleep(0.1)  # <-- Give it a split second to send
                
                cur_song = cloud.get_var("song_num")
                if cur_song is None:
                    cur_song = random.randint(0, len(track_lengths)-1)
                    log("Could not get the song number, resetting it to a random number.", "red")
                    cloud.set_var("song_num", str(cur_song+1))
                    log("It is now song " + str(cloud.get_var("song_num")))
                    time.sleep(0.1) # <-- Give it a split second to send
                    
                total_time = track_lengths[int(cur_song)] * 100
                cloud.set_var("tracklength", str(total_time))
                time.sleep(0.1)  # <-- Give it a split second to send
                
                total_time /= 100
                log(f"Song length is {total_time} secs")
                log("Sleeping the song out.")
                
                start = time.time()
                next_update = start + 1.0
                last_progress = None
                
                while True:
                    elapsed = time.time() - start
                    current_progress = str(round(elapsed))
                    
                    # Optimization: Only send if the value actually changed!
                    if current_progress != last_progress:
                        cloud.set_var("progress", current_progress)
                        last_progress = current_progress
                    
                    if elapsed >= total_time:
                        break
                    
                    sleep_time = next_update - time.time()
                    if sleep_time > 0:
                        # Slightly increased jitter to keep Scratch's spam filters happy
                        jitter = random.uniform(0.02, 0.08)
                        time.sleep(sleep_time + jitter)
                    
                    next_update += 1.0
                    
                cloud.set_var("song_num", str(random.randint(1, len(track_lengths))))
                time.sleep(0.1) # <-- Safety sleep
                cloud.set_var("ready", "1")
                log("Successfully restarted and chose new song!")
                time.sleep(2)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            try_ += 1
            log(f'Errored: "{e}", try #{try_}', "red")
            time.sleep(3)

threading.Thread(target=run_bot, daemon=True).start()
app.run(host="0.0.0.0", port=11303)