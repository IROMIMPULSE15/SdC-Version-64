import requests
import sys

# The deployed Railway URL
WEBHOOK_URL = "https://sdc-version-64-production.up.railway.app/exotel-webhook"

def simulate_interaction(step_name, data):
    print(f"\n📞 --- Simulating: {step_name} ---")
    try:
        # Exotel sends form data (application/x-www-form-urlencoded)
        response = requests.post(WEBHOOK_URL, data=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response (XML):")
            print(response.text)
            return True
        else:
            print("❌ Failed. Server returned error.")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def run_test():
    print(f"Target URL: {WEBHOOK_URL}")
    print("Checking if server is up...")
    
    # 1. Start Call (Simulate Exotel connecting)
    if simulate_interaction("1. Call Connects (Greeting)", {}):
        pass
    else:
        print("\n⚠️ Server might be down or deploying. Try again in 1 minute.")
        return

    # 2. User says 'Yes'
    simulate_interaction("2. User says 'Yes'", {"SpeechResult": "yes"})

    # 3. User provides time (This triggers email)
    print("\n📧 TRIGGERING EMAIL NOW...")
    simulate_interaction("3. User says 'Tomorrow morning'", {"SpeechResult": "I am free tomorrow morning"})
    
    print("\n✅ Test sequence complete.")
    print("👉 If the server is configured correctly on Railway (with RESEND_API_KEY), you should receive an email now.")

if __name__ == "__main__":
    run_test()
