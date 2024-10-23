


<
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from prophet import Prophet
import os
import pickle
from datetime import datetime, timedelta

# download stock data and cache 
def download_and_cache_stock_data(stock_code, start_date, end_date, interval='1d', cache_dir="stock_cache", force_download=False):
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{stock_code}_{start_date}_{end_date}_{interval}.pkl")
    
    if not force_download and os.path.exists(cache_file):
        print(f"Loading cached data for {stock_code} ({interval})...")
        with open(cache_file, 'rb') as f:
            stock_data = pickle.load(f)
    else:
        print(f"Downloading data for {stock_code} ({interval})...")
        stock_data = yf.download(stock_code, start=start_date, end=end_date, interval=interval)
        if stock_data.empty:
            print(f"Unable to download data for {stock_code}")
            return None
        with open(cache_file, 'wb') as f:
            pickle.dump(stock_data, f)
    
    return stock_data

<<<<<<< HEAD
# 从 CSV 文件中读取股票代码（nasdaq-listed.csv）
df = pd.read_csv('//Users/mi/Desktop/Stock_analysis/nasdaq-listed.csv')
stock_codes2 = df['Symbol'].tolist()
print(stock_codes2)
=======
# function of tec_indicator
def calculate_technical_indicators(stock_data):
    stock_data['MA20'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
    
    delta = stock_data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    stock_data['RSI'] = 100 - (100 / (1 + rs))
    
    stock_data['Daily_Returns'] = stock_data['Close'].pct_change()
    stock_data['Volatility'] = stock_data['Daily_Returns'].std() * np.sqrt(252)
    
    return stock_data

# Plot a Single Stock vs. Market Index with Dual Y-Axis
def plot_stock_vs_market(stock_data, market_data, stock_code, market_code='^GSPC'):
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # closing price 
    ax1.set_xlabel('Date')
    ax1.set_ylabel(f'{stock_code} Close Price', color='tab:blue')
    ax1.plot(stock_data.index, stock_data['Close'], label=f'{stock_code} Close Price', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # the 2nd Y axis to reresent the marketindex
    ax2 = ax1.twinx()
    ax2.set_ylabel(f'{market_code} (Market) Close Price', color='tab:orange')
    ax2.plot(market_data.index, market_data['Close'], label=f'{market_code} (Market) Close Price', color='tab:orange', linestyle='--')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    fig.tight_layout()  # automatically adjust layout
    plt.title(f'{stock_code} vs {market_code} Stock Price Comparison')
    plt.show()

# multiple stocks on the same chart for comparison
def plot_multiple_stocks_on_single_chart(stock_data_dict):
    plt.figure(figsize=(10, 6))
    
    for stock_code, stock_data in stock_data_dict.items():
        plt.plot(stock_data.index, stock_data['Close'], label=f'{stock_code} Close Price')

    plt.title('Stock Prices Comparison')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()

# the chart showning stock changes by year, month, week and day
def plot_composite_stock(stock_code, start_date, end_date):
    # download data
    data_daily, data_weekly, data_monthly, data_yearly = download_stock_data_for_composite(stock_code, start_date, end_date)

    # create 4 sub-graph layout
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # 2x2
    fig.suptitle(f'{stock_code} Stock Price Analysis on Different Time Scales')

    # daily change
    axs[0, 0].plot(data_daily.index, data_daily['Close'], label='Daily Close Price')
    axs[0, 0].set_title('Daily')
    axs[0, 0].set_xlabel('Date')
    axs[0, 0].set_ylabel('Price')
    axs[0, 0].legend()

    # weekly change
    axs[0, 1].plot(data_weekly.index, data_weekly['Close'], label='Weekly Close Price', color='orange')
    axs[0, 1].set_title('Weekly')
    axs[0, 1].set_xlabel('Date')
    axs[0, 1].set_ylabel('Price')
    axs[0, 1].legend()

    # monthly change
    axs[1, 0].plot(data_monthly.index, data_monthly['Close'], label='Monthly Close Price', color='green')
    axs[1, 0].set_title('Monthly')
    axs[1, 0].set_xlabel('Date')
    axs[1, 0].set_ylabel('Price')
    axs[1, 0].legend()

    # annual change
    axs[1, 1].plot(data_yearly.index, data_yearly['Close'], label='Yearly Close Price', color='red')
    axs[1, 1].set_title('Yearly')
    axs[1, 1].set_xlabel('Date')
    axs[1, 1].set_ylabel('Price')
    axs[1, 1].legend()

    plt.tight_layout(rect=[0, 0, 1, 0.95])  # automatically adjust layout
    plt.show()

# download stock data required for composite chart
def download_stock_data_for_composite(stock_code, start_date, end_date):
    data_daily = yf.download(stock_code, start=start_date, end=end_date, interval='1d')
    data_weekly = yf.download(stock_code, start=start_date, end=end_date, interval='1wk')
    data_monthly = yf.download(stock_code, start=start_date, end=end_date, interval='1mo')
    data_yearly = data_daily.resample('Y').last()  # resample daily data to annual data 
    return data_daily, data_weekly, data_monthly, data_yearly

# batch process stock analysis and display it on separate charts and a comparison chart
def stock_analysis_multiple_individual_and_comparison(stock_codes, start_date="2020-01-01", end_date="2024-07-01", interval="1d", force_download=False):
    try:
        # download market data
        market_code = '^GSPC'  # using the S&P500 as the broad market
        market_data = download_and_cache_stock_data(market_code, start_date, end_date, interval=interval, force_download=force_download)
        if market_data is None:
            print(f"Error downloading market data for {market_code}.")
            return
        
        stock_data_dict = {}
        for stock_code in stock_codes:
            stock_data = download_and_cache_stock_data(stock_code, start_date, end_date, interval=interval, force_download=force_download)
            if stock_data is not None:
                # tec_indicator
                stock_data = calculate_technical_indicators(stock_data)
                stock_data_dict[stock_code] = stock_data

                # separate chart for each stock, including market comparison
                print(f"Generating individual chart for {stock_code} and comparing with {market_code}...")
                plot_stock_vs_market(stock_data, market_data, stock_code, market_code)

                # changes of year,month, week and day
                print(f"Generating composite chart for {stock_code}...")
                plot_composite_stock(stock_code, start_date, end_date)
        
        # show all stocks for comparison
        print("Generating comparison chart for all stocks...")
        plot_multiple_stocks_on_single_chart(stock_data_dict)
        
    except Exception as e:
        print(f"Error processing multiple stocks: {e}")

# time range
def get_time_range():
    print("Select the time range for stock analysis:")
    print("1. Last 10 years")
    print("2. Last 50 years")
    print("3. Custom range")
    
    choice = input("Enter your choice (1/2/3): ").strip()
    today = datetime.today()

    if choice == "1":
        start_date = today - timedelta(days=365 * 10)  
    elif choice == "2":
        start_date = today - timedelta(days=365 * 50)  
    elif choice == "3":
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        return start_date, end_date
    else:
        print("Invalid choice. Defaulting to last 10 years.")
        start_date = today - timedelta(days=365 * 10)
    
    end_date = today.strftime("%Y-%m-%d")
    return start_date.strftime("%Y-%m-%d"), end_date

# time interval
def get_interval():
    print("Select the data interval:")
    print("1. Daily (1d)")
    print("2. Weekly (1wk)")
    print("3. Hourly (1h)")
    print("4. Minute (1m) - Note: Limited historical data available")
    
    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == "1":
        return '1d'
    elif choice == "2":
        return '1wk'
    elif choice == "3":
        return '1h'
    elif choice == "4":
        return '1m'
    else:
        print("Invalid choice. Defaulting to Daily (1d).")
        return '1d'

if __name__ == "__main__":
    # enter single or multipul stock codes to view trends
    stock_codes = input("Please enter the stock code (Multiple codes separated by commas, default is AAPL): ").upper().split(',')
    if stock_codes == ['']:
        stock_codes = ['AAPL']  # default

    # get the time range
    start_date, end_date = get_time_range()

    # get the time interval
    interval = get_interval()

    # single, composite, and comparison charts
    stock_analysis_multiple_individual_and_comparison(stock_codes, start_date=start_date, end_date=end_date, interval=interval, force_download=False)
>>>>>>> 0bd49a4 (initial coding completed)
