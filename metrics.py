"""Return and risk measures on daily simple returns."""
import numpy as np
import pandas as pd

TRADING_DAYS = 252


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().iloc[1:]


def daily_rf(rf_annual: float) -> float:
    return (1 + rf_annual) ** (1 / TRADING_DAYS) - 1


def annual_return(r: pd.Series) -> float:
    """Compound annual growth rate."""
    years = len(r) / TRADING_DAYS
    return float((1 + r).prod() ** (1 / years) - 1)


def annual_volatility(r: pd.Series) -> float:
    return float(r.std() * np.sqrt(TRADING_DAYS))


def sharpe_ratio(r: pd.Series, rf_annual: float = 0.0) -> float:
    excess = r - daily_rf(rf_annual)
    return float(excess.mean() / excess.std() * np.sqrt(TRADING_DAYS))


def drawdown(r: pd.Series) -> pd.Series:
    """Fall from the previous peak of the wealth curve, starting from 1."""
    wealth = (1 + r).cumprod()
    peak = wealth.cummax().clip(lower=1.0)
    return wealth / peak - 1


def max_drawdown(r: pd.Series) -> float:
    return float(drawdown(r).min())


def beta_alpha(r: pd.Series, m: pd.Series, rf_annual: float = 0.0) -> tuple[float, float]:
    """CAPM beta and annualised alpha from daily excess returns."""
    rf = daily_rf(rf_annual)
    er, em = r - rf, m - rf
    beta = er.cov(em) / em.var()
    alpha = (er.mean() - beta * em.mean()) * TRADING_DAYS
    return float(beta), float(alpha)


def rolling_beta(r: pd.Series, m: pd.Series, window: int = 126) -> pd.Series:
    return r.rolling(window).cov(m) / m.rolling(window).var()


def summary(returns: pd.DataFrame, benchmark: str, rf_annual: float = 0.0) -> pd.DataFrame:
    m = returns[benchmark]
    rows = []
    for col in returns.columns:
        r = returns[col]
        beta, alpha = beta_alpha(r, m, rf_annual)
        rows.append({
            "ticker": col,
            "annual_return": annual_return(r),
            "annual_volatility": annual_volatility(r),
            "sharpe": sharpe_ratio(r, rf_annual),
            "max_drawdown": max_drawdown(r),
            "beta": beta,
            "alpha": alpha,
            "correlation": float(r.corr(m)),
        })
    return pd.DataFrame(rows).set_index("ticker")
