import datetime
from typing import Dict
import yfinance as yf

_PRICE_CACHE: Dict[str, dict] = {}
_CACHE_TTL  : int             = 30

def get_current_price(ticker: str) -> (float, str):
    now = datetime.datetime.now()

    if ticker in _PRICE_CACHE:
        entry = _PRICE_CACHE[ticker]
        if (now - entry["ts"]).total_seconds() < _CACHE_TTL:
            return entry["price"], entry["sector"]

    data   = yf.Ticker(ticker)
    price  = float(data.history(period="1d")['Close'].iloc[-1])
    sector = data.info.get("sector", "Other")

    _PRICE_CACHE[ticker] = {
        "price" : price,
        "ts"    : now,
        "sector": sector
    }
    return price, sector