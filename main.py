from flask import Flask, jsonify
import threading
import scratchattach as sa
import time
import random
import os
import warnings
import math
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
#if its giving you a keyerrr with something to do with the language, uncomment above line

app = Flask(__name__)

status = ['<span style="color:gold">Booting...</span>']
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>cloudradio Logs</title>
        <style>
            body { background-color: #1e1e1e; color: #d4d4d4; font-family: monospace; padding: 20px; }
            #logs { font-size: 22px; white-space: pre-wrap; word-wrap: break-word; }
        </style>
    </head>
    <body>
        <div id="logs">Loading logs...</div>

        <script>
            function fetchLogs() {
                fetch('/raw_logs')
                    .then(response => response.text())
                    .then(data => {
                        const logDiv = document.getElementById('logs');
                        logDiv.innerHTML = data;
                        
                        window.scrollTo(0, document.body.scrollHeight);
                    });
            }
            fetchLogs();
            setInterval(fetchLogs, 1000);
        </script>
    </body>
    </html>
    """

@app.route('/raw_logs')
def raw_logs():
    return "\n".join(status[-150:])

in_song = False
def log(msg, color="grey"):
    global status
    if in_song:
        status[-1] = f'<span style="color:{color}">{msg}</span>'
    else:
        status.append(f'<span style="color:{color}">{msg}</span>')
    #print(msg)

track_lengths = [147.53, 354.02, 175.2, 162.04, 183.44, 193.37, 185.56, 235.55, 261.75, 189.86, 151.35, 208.08]
print(os.getenv("SCRATCH_USER"))
def run_bot():
    global status, in_song
    try_ = 0
    while True:
        if try_ != 0:
            log("Reconnecting...", "gold")
        try:
            item_bag = list(range(len(track_lengths)))
            def grab_from_bag():
                nonlocal item_bag
                if len(item_bag) == 0:
                    item_bag = list(range(len(track_lengths)))
                return item_bag.pop(random.randint(0, len(item_bag) - 1))
            
            try:
                session = sa.login(os.getenv("SCRATCH_USER"), os.getenv("SCRATCH_PASS"))
                log("Managed to login via username and password.", "gold")
            except:
                log("Couldn't login via username and password, using session id", "red")
                session = sa.login_by_id(os.getenv("SC_SESS_ID"))
            
            cloud = session.connect_cloud(project_id="1334822091")
            log("Cloud is ready", "lime")
            
            cur_song = grab_from_bag()
            cloud.set_var("song_num", str(cur_song + 1))
            
            while True:
                log("Starting new phase...")
                time.sleep(0.5)
                
                log("It is now song " + str(cur_song+1), "green")
                    
                total_time = track_lengths[int(cur_song)] * 100
                cloud.set_var("tracklength", str(total_time))
                time.sleep(0.5)
                
                total_time /= 100
                log(f"Song length is {total_time} secs")
                log("Sleeping the song out.")
                
                start = time.time()
                next_update = start + 1.0
                last_progress = None
                
                cloud.set_var("ready", "0")
                
                log(f"Progress: 0/{total_time}")
                in_song = True
                
                while True:
                    elapsed = time.time() - start
                    current_progress = str(round(elapsed, 2) * 100)
                    
                    if current_progress != last_progress:
                        cloud.set_var("progress", current_progress)
                        last_progress = current_progress
                        log(f"Progress: {float(current_progress)/100}/{total_time}")
                    
                    if elapsed >= total_time:
                        break
                    
                    sleep_time = next_update - time.time()
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                    next_update += 1.0
                    
                in_song = False
                
                new_song = grab_from_bag() + 1
                cur_song = new_song - 1
                cloud.set_var("song_num", str(new_song))
                time.sleep(0.2)
                
                total_time = track_lengths[cur_song] * 100
                cloud.set_var("tracklength", str(total_time))
                time.sleep(0.2)
                
                cloud.set_var("progress", "0")
                time.sleep(0.2)
                
                cloud.set_var("ready", "1")
                time.sleep(4.0)
                
        except Exception as e:
            in_song = False
            import traceback
            traceback.print_exc()
            try_ += 1
            log(f'Errored: "{e}", try #{try_}', "red")
            time.sleep(3)

threading.Thread(target=run_bot, daemon=True).start()
app.run(host="0.0.0.0", port=11303)