"""Moving-average crossover compared with buy and hold."""
import pandas as pd

import metrics


def sma_crossover(prices: pd.Series, short: int = 50, long: int = 200, cost_bps: float = 5.0) -> pd.DataFrame:
    """Hold the asset while the short moving average is above the long one.

    The signal from day t's close is applied to the return from t to t+1, so the
    strategy never uses a price it could not have seen. Each change of position
    costs cost_bps basis points.
    """
    if short >= long:
        raise ValueError("short window must be shorter than long window")
    sma_short = prices.rolling(short).mean()
    sma_long = prices.rolling(long).mean()
    signal = (sma_short > sma_long).astype(float)

    df = pd.DataFrame({"price": prices, "signal": signal, "asset_return": prices.pct_change()})
    df["position"] = df["signal"].shift(1)
    first = sma_long.first_valid_index()
    df = df.loc[first:].iloc[1:].copy()  # start once the long average exists

    trades = df["position"].diff().fillna(df["position"]).abs()
    df["trade"] = trades
    df["strategy_return"] = df["position"] * df["asset_return"] - trades * cost_bps / 10_000
    return df


def compare(df: pd.DataFrame, rf_annual: float = 0.0) -> dict:
    """Strategy and buy-and-hold measures over the same days."""
    out = {"start": df.index[0].date(), "end": df.index[-1].date(),
           "trades": int(df["trade"].sum()), "time_in_market": float(df["position"].mean())}
    for name, col in [("strategy", "strategy_return"), ("buy_hold", "asset_return")]:
        r = df[col]
        out[f"{name}_annual_return"] = metrics.annual_return(r)
        out[f"{name}_volatility"] = metrics.annual_volatility(r)
        out[f"{name}_sharpe"] = metrics.sharpe_ratio(r, rf_annual)
        out[f"{name}_max_drawdown"] = metrics.max_drawdown(r)
    return out
