import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import pytz

_ET = pytz.timezone("US/Eastern")

def build_email_body(
    ticker: str,
    action: str,
    confidence: float,
    price: float,
    tech: dict,
    sentiment: dict,
) -> str:
    details = tech.get("details", {})
    now_et = datetime.now(_ET).strftime("%Y-%m-%d %H:%M ET")
    volume_str = "Yes" if details.get("volume_spike") else "No"

    return (
        f"Ticker:       {ticker}\n"
        f"Action:       {action}\n"
        f"Confidence:   {confidence}\n"
        f"Price:        ${price:.2f}\n"
        f"RSI:          {details.get('rsi', 'N/A')}\n"
        f"MACD:         {details.get('macd_signal', 'N/A')}\n"
        f"Bollinger:    {details.get('bb_signal', 'N/A')}\n"
        f"Volume Spike: {volume_str}\n"
        f"Sentiment:    {sentiment.get('score', 0.5):.2f} ({sentiment.get('headline_count', 0)} headlines)\n"
        f"Time:         {now_et}\n"
    )

def send_alert(
    ticker: str,
    price: float,
    signal: dict,
    tech: dict,
    sentiment: dict,
    config: dict,
) -> None:
    """Send buy/sell alert email via SMTP."""
    action = signal["action"]
    confidence = signal["confidence"]
    email_cfg = config["email"]

    subject = f"[{action}] {ticker} — High Confidence Signal ({confidence})"
    body = build_email_body(ticker, action, confidence, price, tech, sentiment)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_cfg["sender"]
    msg["To"] = email_cfg["recipient"]

    with smtplib.SMTP(email_cfg["smtp_host"], email_cfg["smtp_port"]) as server:
        server.starttls()
        server.login(email_cfg["sender"], email_cfg["password"])
        server.sendmail(email_cfg["sender"], email_cfg["recipient"], msg.as_string())
