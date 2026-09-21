import pandas as pd
import numpy as np
import pytest
from technical import analyze_technical

def _make_df(n=60, trend="up"):
    """Create synthetic OHLCV data with realistic RSI values.

    Uptrend pattern: extended rally then sharp pullback -> RSI < 30 (oversold/bullish).
    Downtrend pattern: extended decline then sharp bounce -> RSI > 70 (overbought/bearish).
    These align with the spec's binary RSI thresholds for bullish/bearish classification.
    """
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    close = np.ones(n)
    if trend == "up":
        # Extended uptrend followed by a sharp pullback leaves RSI oversold (<30)
        for i in range(1, n):
            if i < n - 12:
                close[i] = close[i - 1] * 1.005   # sustained rally
            else:
                close[i] = close[i - 1] * 0.975   # sharp pullback -> oversold
    elif trend == "down":
        # Extended downtrend followed by a sharp bounce leaves RSI overbought (>70)
        for i in range(1, n):
            if i < n - 12:
                close[i] = close[i - 1] * 0.995   # sustained decline
            else:
                close[i] = close[i - 1] * 1.025   # sharp bounce -> overbought
    else:
        close = np.ones(n) * 1.5
    df = pd.DataFrame({
        "Open": close * 0.99,
        "High": close * 1.01,
        "Low": close * 0.98,
        "Close": close,
        "Volume": np.ones(n) * 1_000_000,
    }, index=dates)
    return df

def test_returns_required_keys():
    result = analyze_technical(_make_df())
    assert "score" in result
    assert "direction" in result
    assert "details" in result

def test_score_range():
    result = analyze_technical(_make_df())
    assert 0.0 <= result["score"] <= 1.0

def test_direction_values():
    result = analyze_technical(_make_df())
    assert result["direction"] in ("bullish", "bearish", "neutral")

def test_insufficient_data_returns_neutral():
    df = _make_df(n=10)
    result = analyze_technical(df)
    assert result["score"] == 0.5
    assert result["direction"] == "neutral"

def test_volume_spike_detected():
    df = _make_df(n=60)
    # Make last row volume 3x the average
    df.iloc[-1, df.columns.get_loc("Volume")] = 3_000_000
    result = analyze_technical(df)
    assert result["details"]["volume_spike"] is True

def test_uptrend_bullish_score():
    result = analyze_technical(_make_df(n=60, trend="up"))
    # Strong uptrend should produce score above neutral
    assert result["score"] >= 0.5

def test_downtrend_bearish_score():
    result = analyze_technical(_make_df(n=60, trend="down"))
    # Strong downtrend should produce score below or at neutral
    assert result["score"] <= 0.5
