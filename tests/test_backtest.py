import numpy as np
import pandas as pd
import pytest

import backtest

DAYS = pd.bdate_range("2020-01-01", periods=400)


def test_rising_prices_stay_invested():
    prices = pd.Series(np.linspace(100, 200, len(DAYS)), index=DAYS)
    df = backtest.sma_crossover(prices, 5, 20, cost_bps=0)
    assert df["position"].eq(1).all()
    assert np.allclose(df["strategy_return"], df["asset_return"])


def test_signal_is_applied_the_next_day():
    prices = pd.Series(np.r_[np.linspace(100, 150, 200), np.linspace(150, 80, 200)], index=DAYS)
    df = backtest.sma_crossover(prices, 5, 20, cost_bps=0)
    assert (df["position"] == df["signal"].shift(1)).iloc[1:].all()


def test_no_look_ahead():
    """Changing tomorrow's price must not change today's position."""
    rng = np.random.default_rng(0)
    prices = pd.Series(100 * np.cumprod(1 + rng.normal(0, 0.02, len(DAYS))), index=DAYS)
    changed = prices.copy()
    changed.iloc[300:] *= 3
    a = backtest.sma_crossover(prices, 10, 50)
    b = backtest.sma_crossover(changed, 10, 50)
    assert a["position"].loc[: DAYS[300]].equals(b["position"].loc[: DAYS[300]])


def test_costs_are_charged_per_trade():
    prices = pd.Series(np.r_[np.linspace(100, 150, 200), np.linspace(150, 80, 200)], index=DAYS)
    free = backtest.sma_crossover(prices, 5, 20, cost_bps=0)
    paid = backtest.sma_crossover(prices, 5, 20, cost_bps=10)
    diff = free["strategy_return"] - paid["strategy_return"]
    assert diff.sum() == pytest.approx(paid["trade"].sum() * 0.001)
    assert paid["trade"].sum() >= 2  # enters at the start, exits after the turn


def test_short_window_must_be_shorter():
    prices = pd.Series(np.linspace(100, 200, len(DAYS)), index=DAYS)
    with pytest.raises(ValueError):
        backtest.sma_crossover(prices, 50, 20)
