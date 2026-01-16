import pandas as pd
import time
import requests
import os

# Optional: load env vars if running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

EXOTEL_SID = os.getenv("EXOTEL_SID")
EXOTEL_TOKEN = os.getenv("EXOTEL_TOKEN")
CALLER_ID = os.getenv("EXOTEL_CALLER_ID")

def make_call(to_number):
    url = f"https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls/connect.json"
    data = {
        "From": CALLER_ID,
        "To": to_number,
        "Url": "https://sdc-version-64-production.up.railway.app/exotel-webhook"
    }
    # Note: requests.post auth handles basic auth automatically with tuple
    try:
        response = requests.post(url, data=data, auth=(EXOTEL_SID, EXOTEL_TOKEN))
        print(f"Calling {to_number}: Status {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"Failed to call {to_number}: {e}")


if __name__ == "__main__":
    if not os.path.exists("contacts.csv"):
        print("Error: contacts.csv not found.")
    else:
        df = pd.read_csv("contacts.csv")

        # Basic validation to ensure 'phone' column exists
        if "phone" in df.columns:
            for number in df["phone"]:
                # Ensure number is string and strip whitespace
                clean_number = str(number).strip()
                if clean_number: 
                    make_call(clean_number)
                    print("Waiting 90 seconds before next call...")
                    time.sleep(90)  # wait for call to finish
        else:
             print("Error: 'phone' column not found in contacts.csv")
