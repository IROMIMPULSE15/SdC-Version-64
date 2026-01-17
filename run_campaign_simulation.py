import requests
import time
import pandas as pd
import random

# CONFIG
WEBHOOK_URL = "https://sdc-version-64-production.up.railway.app/exotel-webhook"

# SCENARIOS
SCENARIOS = {
    "Lead_1": {
        "phone": "+918055118954", 
        "behavior": ["yes", "I am free tomorrow at 10 AM"],
        "expected_result": "EMAIL SENT"
    },
    "Lead_2": {
        "phone": "+919812345678", 
        "behavior": ["no"],
        "expected_result": "NO EMAIL"
    }
}

def simulate_webhook_call(step_desc, speech_input=None):
    """Simulates a single interaction with the Railway server."""
    data = {}
    if speech_input:
        data["SpeechResult"] = speech_input
    
    print(f"      👉 User says: '{speech_input or '(Silence)'}'")
    try:
        resp = requests.post(WEBHOOK_URL, data=data)
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"      ❌ Server Error {resp.status_code}")
            return None
    except Exception as e:
        print(f"      ❌ Connection failed: {e}")
        return None

def run_simulation():
    print("🚀 STARTING REALISTIC 2-PERSON CAMPAIGN SIMULATION\n")

    # 1. READ CSV (Simulating call_queue.py logic partially)
    try:
        df = pd.read_csv("contacts.csv")
    except:
        print("❌ Error: contacts.csv not found.")
        return

    for idx, row in df.iterrows():
        phone = str(row['phone']).strip()
        
        # Match CSV phone to our Scenario map (using partial match fallback if needed)
        scenario_key = None
        for key, val in SCENARIOS.items():
            if val["phone"] in phone or phone in val["phone"]:
                scenario_key = key
                break
        
        if not scenario_key:
            print(f"⚠️ Skipping {phone} (No scenario defined)")
            continue

        scenario = SCENARIOS[scenario_key]
        print(f"==================================================")
        print(f"📞 CALLING PERSON #{idx+1} ({scenario_key}) -> {phone}")
        print(f"   Goal: {scenario['expected_result']}")
        print(f"==================================================")

        # STEP A: INITIAL GREETING (System speaks first)
        response = simulate_webhook_call("Greeting")
        if response and "<Say>Hello" in response:
            print("   ✅ Bot: Hello. I am calling on behalf of SunRise...")
        else:
            print("   ❌ Bot failed greeting.")
            continue

        time.sleep(1)

        # STEP B: USER RESPONSE (Interest)
        user_response_1 = scenario["behavior"][0] # "yes" or "no"
        response = simulate_webhook_call("Interest Check", user_response_1)
        
        if "yes" in user_response_1:
            if response and "My owner will contact" in response:
                 print("   ✅ Bot: Great! May I know what time...")
                 
                 # STEP C: TIME INPUT
                 time.sleep(1)
                 user_response_2 = scenario["behavior"][1]
                 response = simulate_webhook_call("Time Capture", user_response_2)
                 
                 if response and "Triggering email" in response: # wait, our server returns visual XML only
                     # We can't see server logs, but we check if it acknowledged
                     pass
                 
                 if "Thank you" in response:
                     print("   ✅ Bot: Thank you. Shared availability.")
                     print("   📧 (Email should have been sent!)")
                 else:
                     print("   ❌ Bot logic error on time capture.")
                     
            else:
                 print("   ❌ Bot logic error on 'Yes'.")

        elif "no" in user_response_1:
             if response and "No problem" in response:
                 print("   ✅ Bot: No problem. Have a nice day.")
             else:
                 print("   ❌ Bot logic error on 'No'.")

        print("\n   [Call Ended]\n")
        time.sleep(2) # Pause between calls

    print("✅ CAMPAIGN FINISHED.")

if __name__ == "__main__":
    run_simulation()
