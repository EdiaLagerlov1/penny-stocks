from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from newsapi import NewsApiClient

_analyzer = SentimentIntensityAnalyzer()

def _vader_score_headlines(headlines: list[str]) -> float:
    """Score a list of headlines with VADER. Returns 0–1 (0=negative, 0.5=neutral, 1=positive)."""
    if not headlines:
        return 0.5
    scores = [_analyzer.polarity_scores(h)["compound"] for h in headlines]
    avg = sum(scores) / len(scores)
    # Normalize from [-1, 1] to [0, 1]
    return round((avg + 1) / 2, 4)

def _score_to_direction(score: float) -> str:
    if score >= 0.65:
        return "bullish"
    elif score <= 0.35:
        return "bearish"
    return "neutral"

def analyze_sentiment(ticker: str, newsapi_key: str) -> dict:
    """
    Fetch recent headlines for ticker and score with VADER.

    Returns:
        {
            "score": float (0–1),
            "direction": "bullish" | "bearish" | "neutral",
            "headline_count": int,
        }
    """
    neutral = {"score": 0.5, "direction": "neutral", "headline_count": 0}
    try:
        client = NewsApiClient(api_key=newsapi_key)
        from_dt = (datetime.utcnow() - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")
        response = client.get_everything(
            q=ticker,
            from_param=from_dt,
            language="en",
            sort_by="publishedAt",
            page_size=10,
        )
        articles = response.get("articles", [])
        headlines = [a["title"] for a in articles if a.get("title")]
        if not headlines:
            return neutral
        score = _vader_score_headlines(headlines)
        return {
            "score": score,
            "direction": _score_to_direction(score),
            "headline_count": len(headlines),
        }
    except Exception:
        return neutral
