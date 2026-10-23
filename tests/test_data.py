import sys
import types

import numpy as np
import pandas as pd

import data


def fake_yfinance(calls):
    """Stand-in for yfinance.download, which returns (field, ticker) columns."""
    def download(tickers, start, end, auto_adjust, progress):
        calls.append(list(tickers))
        days = pd.bdate_range(start, periods=5)
        cols = pd.MultiIndex.from_product([["Close", "Open"], tickers], names=["Price", "Ticker"])
        return pd.DataFrame(np.arange(5 * len(cols), dtype=float).reshape(5, -1) + 1, index=days, columns=cols)
    return types.SimpleNamespace(download=download)


def test_downloads_once_then_uses_cache(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setitem(sys.modules, "yfinance", fake_yfinance(calls))
    first = data.load_prices(["AAA", "SPY"], "2020-01-01", "2020-02-01", tmp_path)
    second = data.load_prices(["AAA", "SPY"], "2020-01-01", "2020-02-01", tmp_path)
    assert calls == [["AAA", "SPY"]]
    assert list(first.columns) == ["AAA", "SPY"]
    pd.testing.assert_frame_equal(first, second, check_freq=False)
