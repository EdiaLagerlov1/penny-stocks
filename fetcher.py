import pandas as pd
import yfinance as yf
import time

def fetch_ohlcv(ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV data for a ticker. Returns empty DataFrame on failure."""
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
            if df.empty:
                return pd.DataFrame()
            # Handle MultiIndex columns from newer yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df.dropna(inplace=True)
            return df
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2

    return pd.DataFrame()
