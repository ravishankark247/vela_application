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

Demo OTP: `123456`

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
- Any-file chat attachments
- File conversion workspace
- Camera document scanning
- Settings and sign out
- Vela AI Tutor for quizzes, explanations, flashcards, summaries, and study plans

The upload configuration is set to 100 GB per file for the preview. Actual deployments still depend on browser, hosting, storage, and network limits.

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
