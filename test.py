import os
import time
import random
import scratchattach as sa
from dotenv import load_dotenv
import warnings

# Ignore scratchattach login warnings
warnings.filterwarnings('ignore', category=sa.LoginDataWarning)

load_dotenv()

# --- THE SAME WORKAROUND PATCH YOU HAD ---
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


def run_diagnostics():
    print("--- 1. INITIALIZING TESTING ENVIRONMENT ---")
    username = os.getenv("SCRATCH_USER")
    project_id = "1334822091"
    
    if not username:
        print("❌ ERROR: No SCRATCH_USER found in .env file.")
        return

    print(f"Target Account: {username}")
    print(f"Target Project ID: {project_id}")

    # --- CONNECT TO SCRATCH ---
    print("\n--- 2. ATTEMPTING LOGIN ---")
    try:
        session = sa.login(username, os.getenv("SCRATCH_PASS"))
        print("✅ Success: Logged in using Username/Password.")
    except Exception as e:
        print(f"⚠️ Username/Password login failed ({e}). Trying Session ID...")
        try:
            session = sa.login_by_id(os.getenv("SC_SESS_ID"))
            print("✅ Success: Logged in via Session ID.")
        except Exception as e2:
            print(f"❌ FATAL ERROR: Complete login failure. Details: {e2}")
            return

    # --- CONNECT TO CLOUD ---
    print("\n--- 3. INITIALIZING CLOUD CONNECTION ---")
    try:
        cloud = session.connect_cloud(project_id)
        print("✅ Success: Connected to cloud server stream.")
    except Exception as e:
        print(f"❌ FATAL ERROR: Could not connect to project cloud stream. Details: {e}")
        return

    # --- TEST VARIABLE READING ---
    print("\n--- 4. TESTING VARIABLE READS ---")
    
    # Check your specific variable name
    problem_var = "song-#"
    print(f"Reading target variable '{problem_var}'...")
    val = cloud.get_var(problem_var)
    print(f"Result for '{problem_var}': {val} (Type: {type(val).__name__})")
    
    if val is None:
        print("⚠️ Warning: Got None. Testing if we can read ANY cloud variables on this project...")
        # Most cloud projects have a 'ready' or test variable. Let's look at the cloud logs instead:
        try:
            # Let's see if scratchattach can fetch the server's cloud log history
            logs = sa.get_cloud_logs(project_id, limit=3)
            print(f"✅ Success: Project is active. Last user to update cloud: {logs[0]['user'] if logs else 'None'}")
        except Exception as log_err:
            print(f"❌ Failed to get cloud log history: {log_err}")

    # --- TEST VARIABLE WRITING ---
    print("\n--- 5. TESTING VARIABLE WRITING ---")
    test_val = str(random.randint(1, 99))
    
    # Change "ready" to whatever basic alphanumeric cloud variable you have
    target_write_var = "ready" 
    
    print(f"Attempting to write value '{test_val}' to variable '{target_write_var}'...")
    try:
        cloud.set_var(target_write_var, test_val)
        print("➡️ Command sent through scratchattach pipeline. Waiting 2 seconds for server propagation...")
        time.sleep(2)
        
        print("Verifying if write registered on Scratch servers...")
        verification = cloud.get_var(target_write_var)
        print(f"Server says '{target_write_var}' is now: {verification}")
        
        if str(verification) == str(test_val):
            print("\n🎉 SUCCESS! Python communication and Scratch authentication work flawlessly.")
        else:
            print("\n❌ FAILURE: The write command went through without a Python crash, but Scratch REJECTED it.")
            print("👉 Check if your account is banned/muted, has 'New Scratcher' status, or doesn't own the project.")
            
    except Exception as e:
        print(f"❌ FATAL ERROR: Script crashed attempting to send data. Details: {e}")

if __name__ == "__main__":
    run_diagnostics()