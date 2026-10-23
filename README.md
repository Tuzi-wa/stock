# stock

Risk and return of a few stocks against the S&P 500 (SPY), and a test of a 50/200-day moving-average crossover rule against buy and hold.

Prices are daily closes adjusted for splits and dividends, downloaded from Yahoo Finance with `yfinance`. SPY is used as the benchmark because, like the adjusted stock prices, it includes dividends (the `^GSPC` index does not).

## Result

AAPL, MSFT, JPM, XOM and KO, 2015-01-02 to 2024-12-31 (2,516 trading days). Sharpe ratios and alpha use a risk-free rate of 0.

| | annual return | volatility | Sharpe | max drawdown | beta | alpha |
|---|---|---|---|---|---|---|
| AAPL | 26.3% | 28.5% | 0.96 | -38.5% | 1.21 | 10.7% |
| MSFT | 26.6% | 27.1% | 1.00 | -37.1% | 1.23 | 10.3% |
| JPM | 17.6% | 27.4% | 0.73 | -43.6% | 1.12 | 4.5% |
| XOM | 6.0% | 27.8% | 0.35 | -61.3% | 0.87 | -2.3% |
| KO | 7.4% | 17.8% | 0.49 | -37.0% | 0.60 | 0.5% |
| SPY | 13.0% | 17.6% | 0.78 | -33.7% | 1.00 | 0.0% |

Betas are not stable: over rolling 126-day windows (`results/rolling_beta.png`) AAPL moves between about 0.7 and 1.7, and in late 2024 KO drops to about 0 and XOM to about 0.2.

Moving-average crossover: hold the stock while its 50-day average is above the 200-day average, otherwise hold cash. The signal from one day's close is applied to the next day's return, and each change of position costs 5 basis points. The windows are the usual 50/200 and were not tuned. The test starts on 2015-10-19, once the 200-day average exists.

| | trades | time invested | return, rule | return, buy and hold | Sharpe, rule | Sharpe, buy and hold | max drawdown, rule | max drawdown, buy and hold |
|---|---|---|---|---|---|---|---|---|
| AAPL | 9 | 76% | 19.3% | 28.5% | 0.84 | 1.02 | -45.7% | -38.5% |
| MSFT | 9 | 87% | 26.3% | 28.6% | 1.08 | 1.07 | -28.0% | -37.1% |
| JPM | 11 | 74% | 12.7% | 19.0% | 0.65 | 0.76 | -43.6% | -43.6% |
| XOM | 17 | 59% | 3.6% | 7.6% | 0.28 | 0.40 | -42.2% | -61.3% |
| KO | 16 | 75% | 1.8% | 7.8% | 0.19 | 0.50 | -37.0% | -37.0% |
| SPY | 9 | 80% | 9.9% | 14.2% | 0.72 | 0.84 | -33.7% | -33.7% |

The rule earned less than buy and hold for all six and had a lower Sharpe ratio for five of them (MSFT is about equal). It reduced the worst drawdown for XOM and MSFT, but for JPM, KO and SPY the worst drawdown is the same, because the February-March 2020 crash happened before the averages crossed, and for AAPL it was larger.

These five stocks were picked with hindsight, all of them still exist, and it is a single ten-year period, so the returns of AAPL and MSFT in particular say little about what to expect from other stocks.

## Running

```bash
pip install -r requirements.txt
python analyze.py
python analyze.py --tickers NVDA AMZN --start 2018-01-01 --end 2025-01-01 --rf 0.02
```

Tables go to `results/summary.csv` and `results/backtest.csv`, charts to `results/*.png`. Downloaded prices are kept in `data/cache/`, so later runs with the same tickers and dates work offline. `--prices-csv` reads prices from a CSV (date column, then one column per ticker) instead of downloading. `python analyze.py --help` lists the other options (moving-average windows, cost per trade, rolling-beta window).

Tests: `pip install -r requirements-dev.txt`, then `pytest`. They use generated data and do not need a connection.

## Files

```
analyze.py    command line, writes tables and charts
data.py       download and cache prices
metrics.py    returns, volatility, Sharpe, drawdown, beta and alpha
backtest.py   moving-average crossover and buy and hold
plots.py      charts
tests/
results/      output of python analyze.py with the defaults
```
