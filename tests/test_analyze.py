import numpy as np
import pandas as pd

import analyze


def test_runs_on_a_prices_csv(tmp_path):
    rng = np.random.default_rng(0)
    days = pd.bdate_range("2018-01-01", periods=600)
    market = 100 * np.cumprod(1 + rng.normal(0.0004, 0.01, len(days)))
    stock = 50 * np.cumprod(1 + rng.normal(0.0005, 0.015, len(days)))
    path = tmp_path / "prices.csv"
    pd.DataFrame({"AAA": stock, "SPY": market}, index=days).to_csv(path)

    out = tmp_path / "out"
    assert analyze.main(["--tickers", "AAA", "--prices-csv", str(path), "--out", str(out)]) == 0
    summary = pd.read_csv(out / "summary.csv", index_col=0)
    assert list(summary.index) == ["AAA", "SPY"]
    for name in ["backtest.csv", "prices.png", "drawdowns.png", "rolling_beta.png", "backtest.png"]:
        assert (out / name).exists()
