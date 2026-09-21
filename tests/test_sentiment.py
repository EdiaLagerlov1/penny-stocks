import pytest
from unittest.mock import patch, MagicMock
from sentiment import analyze_sentiment, _score_to_direction, _vader_score_headlines

def test_score_to_direction_bullish():
    assert _score_to_direction(0.8) == "bullish"

def test_score_to_direction_bearish():
    assert _score_to_direction(0.2) == "bearish"

def test_score_to_direction_neutral():
    assert _score_to_direction(0.5) == "neutral"

def test_vader_score_headlines_positive():
    headlines = ["Stock soars on excellent results", "Amazing earnings beat"]
    score = _vader_score_headlines(headlines)
    assert score > 0.5

def test_vader_score_headlines_negative():
    headlines = ["Stock crashes on fraud allegations", "Company misses revenue badly"]
    score = _vader_score_headlines(headlines)
    assert score < 0.5

def test_vader_score_empty_returns_neutral():
    assert _vader_score_headlines([]) == 0.5

def test_analyze_sentiment_no_headlines_returns_neutral():
    mock_client = MagicMock()
    mock_client.get_everything.return_value = {"articles": []}
    with patch("sentiment.NewsApiClient", return_value=mock_client):
        result = analyze_sentiment("SNDL", "fakekey")
    assert result["score"] == 0.5
    assert result["direction"] == "neutral"
    assert result["headline_count"] == 0

def test_analyze_sentiment_positive_headlines():
    mock_client = MagicMock()
    mock_client.get_everything.return_value = {
        "articles": [
            {"title": "Stock surges to all-time high after strong earnings"},
            {"title": "Investors celebrate massive gains and bullish outlook"},
        ]
    }
    with patch("sentiment.NewsApiClient", return_value=mock_client):
        result = analyze_sentiment("SNDL", "fakekey")
    assert result["score"] > 0.5
    assert result["direction"] == "bullish"
    assert result["headline_count"] == 2
