import os
import pytest
from main import load_config, is_market_open
from unittest.mock import patch
from datetime import datetime
import pytz

_ET = pytz.timezone("US/Eastern")

def test_market_open_on_weekday_during_hours():
    # Monday 10:00 ET
    dt = _ET.localize(datetime(2024, 1, 8, 10, 0, 0))
    with patch("main.datetime") as mock_dt:
        mock_dt.now.return_value = dt
        assert is_market_open() is True

def test_market_closed_on_weekend():
    # Saturday
    dt = _ET.localize(datetime(2024, 1, 6, 10, 0, 0))
    with patch("main.datetime") as mock_dt:
        mock_dt.now.return_value = dt
        assert is_market_open() is False

def test_market_closed_before_open():
    # Monday 09:00 ET
    dt = _ET.localize(datetime(2024, 1, 8, 9, 0, 0))
    with patch("main.datetime") as mock_dt:
        mock_dt.now.return_value = dt
        assert is_market_open() is False

def test_market_closed_after_close():
    # Monday 17:00 ET
    dt = _ET.localize(datetime(2024, 1, 8, 17, 0, 0))
    with patch("main.datetime") as mock_dt:
        mock_dt.now.return_value = dt
        assert is_market_open() is False

def test_load_config_returns_watchlist(tmp_path, monkeypatch):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("""
watchlist:
  - SNDL
scan_interval_minutes: 15
confidence_threshold_buy: 0.75
confidence_threshold_sell: 0.25
cooldown_hours: 2
newsapi_key: ${NEWSAPI_KEY}
email:
  smtp_host: smtp.gmail.com
  smtp_port: 587
  sender: ${EMAIL_SENDER}
  password: ${EMAIL_PASSWORD}
  recipient: ${EMAIL_RECIPIENT}
""")
    monkeypatch.setenv("NEWSAPI_KEY", "testkey")
    monkeypatch.setenv("EMAIL_SENDER", "a@b.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "secret")
    monkeypatch.setenv("EMAIL_RECIPIENT", "c@d.com")

    config = load_config(str(cfg))
    assert config["watchlist"] == ["SNDL"]
    assert config["newsapi_key"] == "testkey"
    assert config["email"]["sender"] == "a@b.com"
    assert config["confidence_threshold_buy"] == 0.75
