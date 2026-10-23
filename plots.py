import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import metrics  # noqa: E402


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def normalized_prices(prices, benchmark, path):
    fig, ax = plt.subplots(figsize=(9, 5))
    norm = prices / prices.iloc[0] * 100
    for col in norm.columns:
        style = {"color": "black", "linestyle": "--"} if col == benchmark else {}
        ax.plot(norm.index, norm[col], label=col, linewidth=1.2, **style)
    ax.set_yscale("log")
    ax.set_ylabel("value of 100 invested (log scale)")
    ax.legend()
    _save(fig, path)


def drawdowns(returns, benchmark, path):
    fig, ax = plt.subplots(figsize=(9, 5))
    for col in returns.columns:
        style = {"color": "black", "linestyle": "--"} if col == benchmark else {}
        ax.plot(returns.index, metrics.drawdown(returns[col]) * 100, label=col, linewidth=1, **style)
    ax.set_ylabel("drawdown (%)")
    ax.legend()
    _save(fig, path)


def rolling_betas(returns, benchmark, window, path):
    fig, ax = plt.subplots(figsize=(9, 5))
    for col in returns.columns:
        if col != benchmark:
            ax.plot(returns.index, metrics.rolling_beta(returns[col], returns[benchmark], window),
                    label=col, linewidth=1)
    ax.axhline(1.0, color="grey", linewidth=0.8)
    ax.set_ylabel(f"beta vs {benchmark}, rolling {window} days")
    ax.legend()
    _save(fig, path)


def backtests(results, path):
    n = len(results)
    fig, axes = plt.subplots(n, 1, figsize=(9, 2.6 * n), sharex=True, squeeze=False)
    for ax, (ticker, df) in zip(axes[:, 0], results.items()):
        ax.plot(df.index, (1 + df["asset_return"]).cumprod(), label="buy and hold", linewidth=1)
        ax.plot(df.index, (1 + df["strategy_return"]).cumprod(), label="SMA crossover", linewidth=1)
        ax.set_yscale("log")
        ax.set_title(ticker, fontsize=10)
        ax.legend(fontsize=8)
    _save(fig, path)
