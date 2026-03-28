import os
import smtplib
from email.mime.text import MIMEText
import requests


def send_webhook(message: str):
    url = os.getenv("THREATLENS_WEBHOOK_URL", "").strip()
    if not url:
        return False, "webhook not configured"

    payload = {
        "text": message,      # Slack / generic
        "content": message,   # Discord
        "message": message,   # fallback
    }
    try:
        r = requests.post(url, json=payload, timeout=8)
        return r.ok, f"webhook status={r.status_code}"
    except Exception as e:
        return False, f"webhook error={e}"


def send_email(subject: str, body: str):
    host = os.getenv("THREATLENS_SMTP_HOST", "").strip()
    port = int(os.getenv("THREATLENS_SMTP_PORT", "587"))
    user = os.getenv("THREATLENS_SMTP_USER", "").strip()
    password = os.getenv("THREATLENS_SMTP_PASS", "").strip()
    to = os.getenv("THREATLENS_EMAIL_TO", "").strip()
    sender = os.getenv("THREATLENS_EMAIL_FROM", user).strip()
    if not all([host, user, password, to, sender]):
        return False, "email not configured"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    try:
        with smtplib.SMTP(host, port, timeout=10) as s:
            s.starttls()
            s.login(user, password)
            s.sendmail(sender, [to], msg.as_string())
        return True, "email sent"
    except Exception as e:
        return False, f"email error={e}"
