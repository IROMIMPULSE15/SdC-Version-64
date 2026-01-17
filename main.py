from fastapi import FastAPI, Request
from fastapi.responses import Response
import resend
import os

# Optional: load env vars if running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI()

import pandas as pd

resend.api_key = os.getenv("RESEND_API_KEY")
OWNER_EMAIL = os.getenv("OWNER_EMAIL")

# LOAD CONTACTS DB
CONTACTS_DB = {}
if os.path.exists("contacts.csv"):
    try:
        df = pd.read_csv("contacts.csv")
        # Normalize keys: strip spaces, keep as string
        # Assuming 'phone' and 'name' columns exist
        if "phone" in df.columns and "name" in df.columns:
            for _, row in df.iterrows():
                p = str(row["phone"]).strip()
                n = str(row["name"]).strip()
                CONTACTS_DB[p] = n
        print(f"Loaded {len(CONTACTS_DB)} contacts for name lookup.")
    except Exception as e:
        print(f"Error loading contacts.csv: {e}")

if not resend.api_key:
    print("⚠️ CRITICAL: RESEND_API_KEY is missing from environment variables!")

if not OWNER_EMAIL:
    print("⚠️ CRITICAL: OWNER_EMAIL is missing from environment variables!")


def speak(text: str):
    return f"<Say>{text}</Say>"


def send_email(timing, customer_number):
    try:
        # Lookup Name
        # Helper to normalize phone numbers (keep last 10 digits)
        def normalize_phone(p):
            return "".join(filter(str.isdigit, str(p)))[-10:]

        customer_name = "Unknown Name"
        incoming_norm = normalize_phone(customer_number)

        # Iterate over DB to find a match
        for db_phone, db_name in CONTACTS_DB.items():
            if normalize_phone(db_phone) == incoming_norm:
                customer_name = db_name
                break

        html_content = f"""
        <h2>✅ New Solar Lead Captured</h2>
        <p><b>Name:</b> {customer_name}</p>
        <p><b>Number:</b> {customer_number}</p>
        <p><b>Status:</b> Approved (Interest Confirmed)</p>
        <p><b>Preferred Timing:</b> {timing}</p>
        <hr>
        <p><i>This customer has explicitly expressed interest and provided a time for a meeting.</i></p>
        """

        resend.Emails.send({
            "from": "Solar AI <onboarding@resend.dev>",
            "to": OWNER_EMAIL,
            "subject": f"Lead: {customer_name} - {timing}",
            "html": html_content
        })
        print(f"Email sent for {customer_name} ({customer_number}) at {timing}")
    except Exception as e:
        print(f"Failed to send email: {e}")


@app.post("/exotel-webhook")
async def exotel_webhook(request: Request):
    try:
        form = await request.form()
    except Exception:
        form = {}
    
    user_input = (form.get("Digits") or form.get("SpeechResult") or "").lower()
    customer_number = form.get("From") or "Unknown Number"

    try:
        response = "<Response>"

        # STEP 1: Greeting
        if not user_input:
            response += speak(
                "Hello. I am calling on behalf of SunRise Solar Solutions."
            )
            response += "<Pause length='1'/>"
            response += speak(
                "We specialize in solar installations for homes and private land."
            )
            response += "<Pause length='1'/>"
            response += speak(
                "Are you interested in installing a solar setup on your land? Please say yes or no."
            )
            response += "</Response>"
            return Response(content=response, media_type="application/xml")

        # STEP 2: Interest Decision
        if "yes" in user_input:
            response += speak(
                "That is great to hear."
            )
            response += "<Pause length='1'/>"
            response += speak(
                "My owner will contact you personally."
            )
            response += "<Pause length='1'/>"
            response += speak(
                "May I know what time you will be free after this call?"
            )
            response += "</Response>"
            return Response(content=response, media_type="application/xml")

        # STEP 3: Capture Time & Send Email
        # We check for time keywords, OR if the input is longer than 2 chars and NOT 'yes'/'no' 
        # (Assuming it's a time answer if they are still on the line)
        if any(word in user_input for word in ["morning", "afternoon", "evening", "today", "tomorrow", "at", "pm", "am", "oclock"]):
            send_email(user_input, customer_number)
            response += speak(
                "Thank you. I have shared your availability. You will be contacted soon. Have a great day."
            )
            response += "</Response>"
            return Response(content=response, media_type="application/xml")

        # STEP 4: Not Interested
        if "no" in user_input:
            response += speak(
                "No problem at all. Thank you for your time. Have a nice day."
            )
            response += "</Response>"
            return Response(content=response, media_type="application/xml")

        response += "</Response>"
        return Response(content=response, media_type="application/xml")
    except Exception as e:
        import traceback
        return Response(content=f"Error: {str(e)}\n{traceback.format_exc()}", status_code=200)
