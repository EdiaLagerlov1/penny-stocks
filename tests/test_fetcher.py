import pandas as pd
from fetcher import fetch_ohlcv

def test_fetch_ohlcv_returns_dataframe():
    df = fetch_ohlcv("SNDL", period="5d", interval="1d")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        assert col in df.columns

def test_fetch_ohlcv_bad_ticker_returns_empty():
    df = fetch_ohlcv("INVALIDTICKER_XYZ_999")
    assert isinstance(df, pd.DataFrame)
    assert df.empty
