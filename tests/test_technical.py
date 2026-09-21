import pandas as pd
import numpy as np
import pytest
from technical import analyze_technical

def _make_df(n=60, trend="up"):
    """Create synthetic OHLCV data."""
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    if trend == "up":
        close = np.linspace(1.0, 2.0, n)
    elif trend == "down":
        close = np.linspace(2.0, 1.0, n)
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
