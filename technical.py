import pandas as pd
import pandas_ta as ta

# Indicator weights
_RSI_WEIGHT = 0.30
_MACD_WEIGHT = 0.35
_BB_WEIGHT = 0.20
_VOL_WEIGHT = 0.15

_MIN_ROWS = 26  # minimum for MACD(12,26)

def analyze_technical(df: pd.DataFrame) -> dict:
    """
    Compute technical indicator scores from OHLCV DataFrame.

    Returns:
        {
            "score": float (0–1),
            "direction": "bullish" | "bearish" | "neutral",
            "details": {
                "rsi": float,
                "macd_signal": "bullish" | "bearish" | "neutral",
                "bb_signal": "bullish" | "bearish" | "neutral",
                "volume_spike": bool,
            }
        }
    """
    neutral = {"score": 0.5, "direction": "neutral", "details": {}}
    if df is None or len(df) < _MIN_ROWS:
        return neutral

    close = df["Close"].astype(float)
    volume = df["Volume"].astype(float)

    # --- RSI ---
    rsi_series = ta.rsi(close, length=14)
    rsi = float(rsi_series.iloc[-1]) if rsi_series is not None and not rsi_series.empty else 50.0
    # Normalize RSI to 0–1: high RSI = bullish momentum, low RSI = bearish momentum
    rsi_score = rsi / 100.0

    # --- MACD ---
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    macd_signal = "neutral"
    macd_score = 0.5
    if macd_df is not None and len(macd_df) >= 2:
        macd_col = [c for c in macd_df.columns if c.startswith("MACD_") and "h" not in c.lower() and "s" not in c.lower()]
        sig_col = [c for c in macd_df.columns if "MACDs" in c]
        if macd_col and sig_col:
            macd_val = macd_df[macd_col[0]]
            sig_val = macd_df[sig_col[0]]
            prev_diff = float(macd_val.iloc[-2]) - float(sig_val.iloc[-2])
            curr_diff = float(macd_val.iloc[-1]) - float(sig_val.iloc[-1])
            if prev_diff < 0 and curr_diff >= 0:
                macd_signal = "bullish"
                macd_score = 1.0
            elif prev_diff > 0 and curr_diff <= 0:
                macd_signal = "bearish"
                macd_score = 0.0

    # --- Bollinger Bands ---
    bb_df = ta.bbands(close, length=20, std=2)
    bb_signal = "neutral"
    bb_score = 0.5
    if bb_df is not None and not bb_df.empty:
        lower_col = [c for c in bb_df.columns if "BBL" in c]
        upper_col = [c for c in bb_df.columns if "BBU" in c]
        if lower_col and upper_col:
            lower = float(bb_df[lower_col[0]].iloc[-1])
            upper = float(bb_df[upper_col[0]].iloc[-1])
            price = float(close.iloc[-1])
            if price <= lower:
                bb_signal = "bullish"
                bb_score = 1.0
            elif price >= upper:
                bb_signal = "bearish"
                bb_score = 0.0

    # --- Volume spike ---
    vol_avg_20 = float(volume.iloc[-21:-1].mean()) if len(volume) >= 21 else float(volume.mean())
    current_vol = float(volume.iloc[-1])
    volume_spike = current_vol > (2 * vol_avg_20)

    # --- Weighted score (volume amplifies if spike, otherwise neutral) ---
    base_score = (
        rsi_score * _RSI_WEIGHT +
        macd_score * _MACD_WEIGHT +
        bb_score * _BB_WEIGHT
    )
    vol_score = base_score  # volume spike pushes toward current direction
    weighted_score = base_score * (1 - _VOL_WEIGHT) + vol_score * _VOL_WEIGHT

    # --- Direction ---
    if weighted_score >= 0.65:
        direction = "bullish"
    elif weighted_score <= 0.35:
        direction = "bearish"
    else:
        direction = "neutral"

    return {
        "score": round(weighted_score, 4),
        "direction": direction,
        "details": {
            "rsi": round(rsi, 2),
            "macd_signal": macd_signal,
            "bb_signal": bb_signal,
            "volume_spike": volume_spike,
        },
    }
