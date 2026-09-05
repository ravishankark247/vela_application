"""SMS verification helpers for Vela."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request


def configured() -> bool:
    return all(os.getenv(name, "").strip() for name in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_VERIFY_SERVICE_SID"))


def _request(action: str, phone: str, code: str | None = None) -> bool:
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    service_sid = os.environ["TWILIO_VERIFY_SERVICE_SID"]
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
    except (urllib.error.HTTPError, urllib.error.URLError):
        return False


def send_code(phone: str) -> bool:
    return _request("verifications", phone)


def verify_code(phone: str, code: str) -> bool:
    return _request("verification_check", phone, code)
