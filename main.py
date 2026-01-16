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

resend.api_key = os.getenv("RESEND_API_KEY")
OWNER_EMAIL = os.getenv("OWNER_EMAIL")


def speak(text: str):
    return f"<Say>{text}</Say>"


def send_email(timing):
    try:
        resend.Emails.send({
            "from": "Solar AI <onboarding@resend.dev>",
            "to": OWNER_EMAIL,
            "subject": "🔥 Interested Solar Lead",
            "html": f"""
            <p>A customer is interested in solar installation.</p>
            <p><b>Available Time:</b> {timing}</p>
            """
        })
        print(f"Email sent for timing: {timing}")
    except Exception as e:
        print(f"Failed to send email: {e}")


@app.post("/exotel-webhook")
async def exotel_webhook(request: Request):
    try:
        form = await request.form()
    except Exception:
        form = {}
    
    user_input = (form.get("Digits") or form.get("SpeechResult") or "").lower()

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
        if any(word in user_input for word in ["morning", "afternoon", "evening", "today", "tomorrow"]):
            send_email(user_input)
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
