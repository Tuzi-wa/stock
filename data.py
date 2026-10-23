"""Daily prices from yfinance, with a CSV copy per ticker so repeated runs work offline."""
from pathlib import Path

import pandas as pd


def _cache_path(cache_dir: Path, ticker: str, start: str, end: str) -> Path:
    safe = ticker.replace("^", "_").replace("/", "_")
    return cache_dir / f"{safe}_{start}_{end}.csv"


def load_prices(tickers, start, end, cache_dir="data/cache", refresh=False) -> pd.DataFrame:
    """Adjusted daily close prices, one column per ticker, rows where every ticker has a price."""
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)

    series, missing = {}, []
    for t in tickers:
        path = _cache_path(cache, t, start, end)
        if path.exists() and not refresh:
            series[t] = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0].rename(t)
        else:
            missing.append(t)

    if missing:
        import yfinance as yf

        raw = yf.download(missing, start=start, end=end, auto_adjust=True, progress=False)
        close = raw["Close"]
        if isinstance(close, pd.Series):  # older yfinance versions, single ticker
            close = close.to_frame(missing[0])
        for t in missing:
            if t not in close.columns or close[t].dropna().empty:
                raise ValueError(f"no price data for {t}")
            s = close[t].dropna().rename(t)
            s.to_csv(_cache_path(cache, t, start, end))
            series[t] = s

    prices = pd.DataFrame(series)[list(tickers)]
    return prices.dropna()


def read_prices_csv(path) -> pd.DataFrame:
    """Prices from a CSV with a date column first and one column per ticker."""
    return pd.read_csv(path, index_col=0, parse_dates=True).dropna()
