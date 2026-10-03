import os
import re
import logging
import yaml
from datetime import datetime, time as dt_time, timezone
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

from fetcher import fetch_ohlcv
from technical import analyze_technical
from sentiment import analyze_sentiment
from combiner import combine_signals
from notifier import send_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

_ET = pytz.timezone("US/Eastern")
_MARKET_OPEN = (9, 30)
_MARKET_CLOSE = (16, 0)

# In-memory cooldown state: {ticker: datetime of last alert}
_cooldown_state: dict = {}

load_dotenv()

def _substitute_env_vars(value):
    """Replace ${VAR} patterns with environment variable values."""
    if isinstance(value, str):
        return re.sub(
            r'\$\{(\w+)\}',
            lambda m: os.environ.get(m.group(1), m.group(0)),
            value
        )
    if isinstance(value, dict):
        return {k: _substitute_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute_env_vars(i) for i in value]
    return value

def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return _substitute_env_vars(raw)


def is_market_open() -> bool:
    now = datetime.now(_ET)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    market_open = dt_time(_MARKET_OPEN[0], _MARKET_OPEN[1])
    market_close = dt_time(_MARKET_CLOSE[0], _MARKET_CLOSE[1])
    return market_open <= now.time() < market_close


def scan(config: dict) -> None:
    if not is_market_open():
        log.info("Market closed — skipping scan.")
        return

    for ticker in config["watchlist"]:
        log.info(f"Scanning {ticker}...")
        try:
            df = fetch_ohlcv(ticker, period="1mo", interval="1d")
            if df.empty:
                log.warning(f"{ticker}: no data returned, skipping.")
                continue

            price = float(df["Close"].iloc[-1])
            tech = analyze_technical(df)
            sent = analyze_sentiment(ticker, config["newsapi_key"])
            signal = combine_signals(ticker, tech, sent, _cooldown_state, config)

            log.info(
                f"{ticker}: action={signal['action']} confidence={signal['confidence']} "
                f"alert={signal['should_alert']}"
            )

            if signal["should_alert"]:
                send_alert(ticker, price, signal, tech, sent, config)
                _cooldown_state[ticker] = datetime.now(timezone.utc)
                log.info(f"{ticker}: alert sent.")

        except Exception as e:
            log.error(f"{ticker}: error during scan — {e}")


def main():
    config = load_config()
    interval = config.get("scan_interval_minutes", 15)

    log.info(f"Starting scanner. Watchlist: {config['watchlist']}. Interval: {interval}min.")
    scan(config)  # run immediately on start

    scheduler = BlockingScheduler()
    scheduler.add_job(scan, "interval", minutes=interval, args=[config])
    scheduler.start()


if __name__ == "__main__":
    main()
