import pytest
from datetime import datetime, timedelta
from combiner import combine_signals

_config = {
    "confidence_threshold_buy": 0.75,
    "confidence_threshold_sell": 0.25,
    "cooldown_hours": 2,
}

def test_buy_signal_fires_when_both_bullish():
    tech = {"score": 0.85, "direction": "bullish", "details": {}}
    sent = {"score": 0.80, "direction": "bullish", "headline_count": 5}
    result = combine_signals("SNDL", tech, sent, {}, _config)
    assert result["action"] == "BUY"
    assert result["should_alert"] is True
    assert result["confidence"] >= 0.75

def test_sell_signal_fires_when_both_bearish():
    tech = {"score": 0.10, "direction": "bearish", "details": {}}
    sent = {"score": 0.15, "direction": "bearish", "headline_count": 3}
    result = combine_signals("SNDL", tech, sent, {}, _config)
    assert result["action"] == "SELL"
    assert result["should_alert"] is True
    assert result["confidence"] <= 0.25

def test_conflicting_directions_suppressed():
    tech = {"score": 0.85, "direction": "bullish", "details": {}}
    sent = {"score": 0.20, "direction": "bearish", "headline_count": 4}
    result = combine_signals("SNDL", tech, sent, {}, _config)
    assert result["should_alert"] is False
    assert result["action"] == "HOLD"

def test_cooldown_suppresses_repeat_alert():
    tech = {"score": 0.85, "direction": "bullish", "details": {}}
    sent = {"score": 0.80, "direction": "bullish", "headline_count": 5}
    cooldown_state = {"SNDL": datetime.utcnow() - timedelta(minutes=30)}
    result = combine_signals("SNDL", tech, sent, cooldown_state, _config)
    assert result["should_alert"] is False

def test_cooldown_expired_allows_alert():
    tech = {"score": 0.85, "direction": "bullish", "details": {}}
    sent = {"score": 0.80, "direction": "bullish", "headline_count": 5}
    cooldown_state = {"SNDL": datetime.utcnow() - timedelta(hours=3)}
    result = combine_signals("SNDL", tech, sent, cooldown_state, _config)
    assert result["should_alert"] is True

def test_hold_when_below_threshold():
    tech = {"score": 0.60, "direction": "neutral", "details": {}}
    sent = {"score": 0.55, "direction": "neutral", "headline_count": 2}
    result = combine_signals("SNDL", tech, sent, {}, _config)
    assert result["action"] == "HOLD"
    assert result["should_alert"] is False
