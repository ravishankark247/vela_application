"""SMS verification helpers for Vela."""

from __future__ import annotations

import base64
import json
import os
import smtplib
from email.message import EmailMessage
import urllib.error
import urllib.parse
import urllib.request

last_error = ""


def _secret(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st

        return str(st.secrets.get(name, "")).strip()
    except (ImportError, FileNotFoundError, KeyError, AttributeError):
        return ""


def configured() -> bool:
    return all(_secret(name) for name in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_VERIFY_SERVICE_SID"))


def email_configured() -> bool:
    return all(_secret(name) for name in ("SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "OTP_FROM_EMAIL"))


def provider() -> str:
    requested = _secret("OTP_PROVIDER").lower()
    if requested == "email" and email_configured():
        return "email"
    if requested == "sms" and configured():
        return "sms"
    if configured():
        return "sms"
    if email_configured():
        return "email"
    return "demo"


def send_email_code(recipient: str, code: str) -> bool:
    global last_error
    last_error = ""
    message = EmailMessage()
    message["Subject"] = "Your Vela verification code"
    message["From"] = _secret("OTP_FROM_EMAIL")
    message["To"] = recipient
    message.set_content(f"Your Vela verification code is {code}. It expires when you request a new code.")
    try:
        with smtplib.SMTP(_secret("SMTP_HOST"), int(_secret("SMTP_PORT")), timeout=15) as server:
            if _secret("SMTP_USE_TLS").lower() != "false":
                server.starttls()
            server.login(_secret("SMTP_USERNAME"), _secret("SMTP_PASSWORD"))
            server.send_message(message)
        return True
    except (OSError, smtplib.SMTPException, ValueError) as error:
        last_error = f"Email provider error: {error}"
        return False


def _request(action: str, phone: str, code: str | None = None) -> bool:
    global last_error
    last_error = ""
    account_sid = _secret("TWILIO_ACCOUNT_SID")
    auth_token = _secret("TWILIO_AUTH_TOKEN")
    service_sid = _secret("TWILIO_VERIFY_SERVICE_SID")
    endpoint = f"https://verify.twilio.com/v2/Services/{service_sid}/Verifications"
    if action == "verification_check":
        endpoint += "/VerificationCheck"
    values = {"To": phone, "Channel": "sms"}
    if code:
        values = {"To": phone, "Code": code}
    request = urllib.request.Request(endpoint, data=urllib.parse.urlencode(values).encode(), method="POST")
    token = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    request.add_header("Authorization", f"Basic {token}")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode())
        return payload.get("status") in {"pending", "approved"}
    except urllib.error.HTTPError as error:
        try:
            details = json.loads(error.read().decode())
            last_error = details.get("message", "Twilio rejected the request.")
        except (json.JSONDecodeError, UnicodeDecodeError):
            last_error = f"SMS provider returned HTTP {error.code}."
        return False
    except urllib.error.URLError:
        last_error = "Could not reach Twilio. Check the deployed app's internet connection."
        return False


def send_code(phone: str) -> bool:
    return _request("verifications", phone)


def verify_code(phone: str, code: str) -> bool:
    return _request("verification_check", phone, code)
