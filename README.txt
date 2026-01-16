# Solar AI Caller System

## Setup

1. **Install Dependencies**
   Run the following command in your terminal:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Open `.env` file and fill in your details:
   - `EXOTEL_SID`: Your Exotel Account SID
   - `EXOTEL_TOKEN`: Your Exotel Account Token
   - `EXOTEL_CALLER_ID`: Your Exotel Virtual Number
   - `RESEND_API_KEY`: Your Resend API Key
   - `OWNER_EMAIL`: The email where you want to receive leads

3. **Manage Contacts**
   Edit `contacts.csv` to add or remove phone numbers.
   Format:
   ```csv
   phone
   +919876543210
   ...
   ```

## Running the System

### 1. Start the Webhook Server (FastAPI)
This handles the logic when a call connects or the user speaks.
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
*Note: For production, this will run on Railway.*

### 2. Start the Calling Queue
This reads the CSV and initiates calls one by one.
```bash
python call_queue.py
```

## Deployment (Railway)

1. Push this folder to GitHub.
2. Create a new project on Railway from the GitHub repo.
3. Add the environment variables from `.env` into Railway's variable settings.
4. Update the `Url` in `call_queue.py` (line 15) to your deployed Railway URL (e.g., `https://your-app.up.railway.app/exotel-webhook`).
