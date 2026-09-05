# Vela Streamlit Chat App

A mobile-responsive WhatsApp-style chat workspace built with Python and Streamlit.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`.

You can also start the Python preview launcher directly:

```bash
python3 preview.py
```

Demo OTP: `123456`

## Real SMS verification

The included demo OTP is used only when Twilio is not configured. For real phone-number verification, create a Twilio Verify service and set these environment variables before starting Vela:

```bash
export TWILIO_ACCOUNT_SID=your-account-sid
export TWILIO_AUTH_TOKEN=your-auth-token
export TWILIO_VERIFY_SERVICE_SID=your-verify-service-sid
python3 preview.py
```

Use phone numbers in international E.164 format, such as `+919876543210`. Never put these credentials in source control. Twilio, the deployed server, and the user's network must all be available for SMS verification and always-online access.

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Open [share.streamlit.io](https://share.streamlit.io).
3. Choose the repository and branch.
4. Set the main file to `app.py`.
5. Deploy.

Streamlit will install `requirements.txt` and use `.streamlit/config.toml` automatically.

## Included sections

- Mobile number and OTP login preview
- One-to-one and group chats
- Search, unread state, online friends, status, and calls
- Voice messages, local microphone recording, video-call camera preview, and voice/video call controls
- Any-file chat attachments
- File conversion workspace
- Camera document scanning
- Settings and sign out
- Vela AI Tutor for quizzes, explanations, flashcards, summaries, and study plans

## Persistent data

The app now creates `vela.db` automatically and stores chats, messages, voice messages, feed posts, likes, and comments across Streamlit reruns and restarts. Set `VELA_DB_PATH` to place the SQLite database on a persistent disk:

```bash
VELA_DB_PATH=/data/vela.db python3 preview.py
```

SQLite is reliable for a single running app server. For multiple users or multiple server instances, replace the storage layer with a hosted PostgreSQL service and object storage for uploaded media. The app cannot keep an internet connection when a device or network is offline; the UI shows a storage warning and continues with session data during a temporary database failure.

The upload configuration is set to 100 GB per file for the preview. Actual deployments still depend on browser, hosting, storage, and network limits.

The voice and video call experience is a local Streamlit preview: it can access the browser microphone and camera, record voice messages, and show call states. Real-time calls between different users require a WebRTC signaling service and a backend, which are outside this single-process preview.

## AI Tutor providers

Vela works without an API key using its built-in offline study helper. To use an OpenAI-compatible provider, add these Streamlit secrets or environment variables:

```text
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

`OPENAI_BASE_URL` can point to another OpenAI-compatible service or local model gateway. API pricing and free-tier availability depend on the provider; no provider offers unlimited free OpenAI API usage.

## APK note

Streamlit deploys a responsive web app, not a native Android APK. The deployed URL can be installed as a phone home-screen app using the browser's Add to Home Screen action. A true APK would require wrapping the deployed URL with a separate Android tool such as Capacitor, Trusted Web Activity, or a native Android project.
