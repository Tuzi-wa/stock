import numpy as np
import pandas as pd
import pytest

import metrics

DAYS = pd.bdate_range("2020-01-01", periods=504)


def test_annual_return_of_constant_growth():
    daily = 1.10 ** (1 / 252) - 1
    r = pd.Series(daily, index=DAYS)
    assert metrics.annual_return(r) == pytest.approx(0.10)


def test_volatility_and_sharpe():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.0004, 0.01, len(DAYS)), index=DAYS)
    assert metrics.annual_volatility(r) == pytest.approx(r.std() * np.sqrt(252))
    assert metrics.sharpe_ratio(r) == pytest.approx(r.mean() / r.std() * np.sqrt(252))
    assert metrics.sharpe_ratio(r, 0.02) < metrics.sharpe_ratio(r)


def test_max_drawdown():
    # 100 -> 120 -> 60 -> 90: largest fall is from 120 to 60
    prices = pd.Series([100, 120, 60, 90], dtype=float)
    r = prices.pct_change().iloc[1:]
    assert metrics.max_drawdown(r) == pytest.approx(-0.5)


def test_drawdown_counts_a_fall_from_the_start():
    r = pd.Series([-0.1, 0.05])
    assert metrics.drawdown(r).iloc[0] == pytest.approx(-0.1)


def test_beta_and_alpha_of_leveraged_series():
    rng = np.random.default_rng(1)
    m = pd.Series(rng.normal(0.0003, 0.01, len(DAYS)), index=DAYS)
    r = 2 * m + 0.0001
    beta, alpha = metrics.beta_alpha(r, m)
    assert beta == pytest.approx(2.0)
    assert alpha == pytest.approx(0.0001 * 252)


def test_rolling_beta():
    rng = np.random.default_rng(2)
    m = pd.Series(rng.normal(0, 0.01, len(DAYS)), index=DAYS)
    rb = metrics.rolling_beta(1.5 * m, m, window=60)
    assert rb.iloc[:59].isna().all()
    assert np.allclose(rb.dropna(), 1.5)


def test_summary_has_benchmark_beta_one():
    rng = np.random.default_rng(3)
    returns = pd.DataFrame(rng.normal(0.0003, 0.01, (len(DAYS), 2)), index=DAYS, columns=["A", "SPY"])
    s = metrics.summary(returns, "SPY")
    assert s.loc["SPY", "beta"] == pytest.approx(1.0)
    assert s.loc["SPY", "correlation"] == pytest.approx(1.0)
