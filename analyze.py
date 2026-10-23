import argparse
from pathlib import Path

import pandas as pd

import backtest
import data
import metrics
import plots


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Risk and return of a few stocks against a benchmark, plus a moving-average backtest.")
    p.add_argument("--tickers", nargs="+", default=["AAPL", "MSFT", "JPM", "XOM", "KO"])
    p.add_argument("--benchmark", default="SPY")
    p.add_argument("--start", default="2015-01-01")
    p.add_argument("--end", default="2025-01-01", help="exclusive")
    p.add_argument("--rf", type=float, default=0.0, help="annual risk-free rate, e.g. 0.02")
    p.add_argument("--short", type=int, default=50, help="short moving average (days)")
    p.add_argument("--long", type=int, default=200, help="long moving average (days)")
    p.add_argument("--cost-bps", type=float, default=5.0, help="cost per change of position, in basis points")
    p.add_argument("--beta-window", type=int, default=126, help="days for the rolling beta")
    p.add_argument("--prices-csv", help="use prices from this CSV instead of downloading")
    p.add_argument("--cache-dir", default="data/cache")
    p.add_argument("--refresh", action="store_true", help="download again even if cached")
    p.add_argument("--out", default="results")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    tickers = [t.upper() for t in args.tickers]
    benchmark = args.benchmark.upper()
    columns = tickers + ([benchmark] if benchmark not in tickers else [])

    if args.prices_csv:
        prices = data.read_prices_csv(args.prices_csv)[columns]
    else:
        prices = data.load_prices(columns, args.start, args.end, args.cache_dir, args.refresh)
    returns = metrics.daily_returns(prices)
    print(f"{len(prices)} trading days, {prices.index[0].date()} to {prices.index[-1].date()}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    summary = metrics.summary(returns, benchmark, args.rf)
    (summary.round(4) + 0.0).to_csv(out / "summary.csv")  # + 0.0 turns -0.0 into 0.0
    print("\nbuy and hold")
    print(summary.round(3).to_string())

    runs = {t: backtest.sma_crossover(prices[t], args.short, args.long, args.cost_bps) for t in columns}
    bt = pd.DataFrame({t: backtest.compare(df, args.rf) for t, df in runs.items()}).T
    bt.index.name = "ticker"
    numeric = [c for c in bt.columns if c not in ("start", "end")]
    bt[numeric] = bt[numeric].apply(pd.to_numeric)
    bt.round(4).to_csv(out / "backtest.csv")
    print(f"\nSMA {args.short}/{args.long} crossover vs buy and hold, {args.cost_bps:g} bps per trade")
    cols = ["trades", "time_in_market", "strategy_annual_return", "buy_hold_annual_return",
            "strategy_sharpe", "buy_hold_sharpe", "strategy_max_drawdown", "buy_hold_max_drawdown"]
    print(bt[cols].round(3).to_string())

    plots.normalized_prices(prices, benchmark, out / "prices.png")
    plots.drawdowns(returns, benchmark, out / "drawdowns.png")
    plots.rolling_betas(returns, benchmark, args.beta_window, out / "rolling_beta.png")
    plots.backtests(runs, out / "backtest.png")
    print(f"\nsaved tables and charts to {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
