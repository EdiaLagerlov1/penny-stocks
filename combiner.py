from datetime import datetime, timedelta

_TECH_WEIGHT = 0.70
_SENT_WEIGHT = 0.30

def combine_signals(
    ticker: str,
    tech: dict,
    sentiment: dict,
    cooldown_state: dict,
    config: dict,
) -> dict:
    """
    Combine technical and sentiment signals into a final action.

    Args:
        ticker: Stock ticker symbol
        tech: Output of analyze_technical()
        sentiment: Output of analyze_sentiment()
        cooldown_state: Dict mapping ticker -> datetime of last alert
        config: App config dict with threshold and cooldown keys

    Returns:
        {"action": "BUY"|"SELL"|"HOLD", "confidence": float, "should_alert": bool}
    """
    hold = {"action": "HOLD", "confidence": 0.5, "should_alert": False}

    tech_score = tech.get("score", 0.5)
    tech_dir = tech.get("direction", "neutral")
    sent_score = sentiment.get("score", 0.5)
    sent_dir = sentiment.get("direction", "neutral")

    # Direction agreement: both must be bullish or both bearish
    if tech_dir == "bullish" and sent_dir != "bullish":
        return hold
    if tech_dir == "bearish" and sent_dir != "bearish":
        return hold
    if tech_dir == "neutral":
        return hold

    # Combined confidence
    confidence = round(tech_score * _TECH_WEIGHT + sent_score * _SENT_WEIGHT, 4)

    buy_threshold = config.get("confidence_threshold_buy", 0.75)
    sell_threshold = config.get("confidence_threshold_sell", 0.25)
    cooldown_hours = config.get("cooldown_hours", 2)

    if confidence >= buy_threshold:
        action = "BUY"
    elif confidence <= sell_threshold:
        action = "SELL"
    else:
        return {**hold, "confidence": confidence}

    # Cooldown check
    last_alert = cooldown_state.get(ticker)
    if last_alert and datetime.utcnow() - last_alert < timedelta(hours=cooldown_hours):
        return {"action": action, "confidence": confidence, "should_alert": False}

    return {"action": action, "confidence": confidence, "should_alert": True}
