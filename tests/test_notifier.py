import pytest
from unittest.mock import patch, MagicMock
from notifier import build_email_body, send_alert

def test_build_email_body_buy():
    body = build_email_body(
        ticker="SNDL",
        action="BUY",
        confidence=0.82,
        price=1.43,
        tech={"details": {"rsi": 28.0, "macd_signal": "bullish", "bb_signal": "bullish", "volume_spike": True}},
        sentiment={"score": 0.72, "headline_count": 8},
    )
    assert "BUY" in body
    assert "SNDL" in body
    assert "0.82" in body
    assert "1.43" in body
    assert "28.0" in body

def test_build_email_body_sell():
    body = build_email_body(
        ticker="MULN",
        action="SELL",
        confidence=0.18,
        price=0.87,
        tech={"details": {"rsi": 74.0, "macd_signal": "bearish", "bb_signal": "bearish", "volume_spike": False}},
        sentiment={"score": 0.22, "headline_count": 3},
    )
    assert "SELL" in body
    assert "MULN" in body

def test_send_alert_calls_smtp(monkeypatch):
    config = {
        "email": {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "sender": "a@b.com",
            "password": "secret",
            "recipient": "c@d.com",
        }
    }
    signal = {"action": "BUY", "confidence": 0.82}
    tech = {"details": {"rsi": 28.0, "macd_signal": "bullish", "bb_signal": "neutral", "volume_spike": False}}
    sentiment = {"score": 0.70, "headline_count": 5}

    mock_smtp = MagicMock()
    with patch("notifier.smtplib.SMTP", return_value=mock_smtp):
        send_alert("SNDL", 1.43, signal, tech, sentiment, config)

    mock_smtp.__enter__.return_value.sendmail.assert_called_once()
