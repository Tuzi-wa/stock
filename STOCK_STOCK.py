# 用户可以通过输入股票名字或代码查看股票走势
import pandas as pd
from pandas_datareader import data

# 从 CSV 文件中读取股票代码（SP500.csv）
df = pd.read_csv('//Users/mi/Desktop/Stock_analysis/SP500.csv')
stock_codes1 = df['Symbol'].tolist()
print(stock_codes1)

# 从 CSV 文件中读取股票代码（nasdaq-listed.csv）
df = pd.read_csv('//Users/mi/Desktop/Stock_analysis/nasdaq-listed.csv')
stock_codes2 = df['Symbol'].tolist()
print(stock_codes2)