import pandas as pd
import numpy as np
import yfinance as yf
import ta
import matplotlib.pyplot as plt

df = yf.download('BDX', start='2019-01-01')

df['shifted'] = df.Close.shift()  # for stop loss 

# half life
from sklearn import linear_model
df_lag = df['Close'].shift(1)
df_delta = df['Close'] - df_lag
lin_reg_model = linear_model.LinearRegression()
df_delta = df_delta.values.reshape(len(df_delta),1)                    
df_lag = df_lag.values.reshape(len(df_lag),1)
lin_reg_model.fit(df_lag[1:], df_delta[1:])                           
half_life = -np.log(2) / lin_reg_model.coef_.item()
# half-life = 16.227080962345063

# moving average over 19 day period (small multiple of half-life)
df['sma'] = df['Close'].rolling(19).mean()
df['std'] = df['Close'].rolling(19).std()
df['upper_bollinger'] = df['sma'] + (2 * df['std'])
df['lower_bollinger'] = df['sma'] - (2 * df['std'])

# RSI over 6 day period
df['rsi'] = ta.momentum.rsi(df.Close, window = 6)

conditions = [(df.rsi < 30) & (df.Close < df.lower_bollinger), (df.rsi > 70) & (df.Close > df.upper_bollinger)]
choices = ['Buy','Sell']
df['signal'] = np.select(conditions,choices)
df.dropna(inplace = True)

df.signal = df.signal.shift() 

position = False
buydates, selldates = [], []
buyprices, sellprices= [], []

for index,row in df.iterrows():
    if not position and row.signal == 'buy':
        buydate.append(index)
        buyprice.append(row.Open)
        position = True
        
    if position:
        if row.signal == 'sell' or row.shifted < 0.95 * buyprice[-1]:  # stop loss
            selldate.append(index)
            sellprice.append(row.Open)
            position = False

# plot
plt.figure(figsize=(10,4))
plt.title('Price Chart & Historical Trades', fontweight="bold")

plt.plot(df.Close)
plt.scatter(df.loc[buydate].index,df.loc[buydate].Close,marker='^',c='g', label='Buy')
plt.scatter(df.loc[selldate].index,df.loc[selldate].Close,marker='v',c='r', label='Sell')
plt.fill_between(df.index,df.lower_bollinger,df.upper_bollinger,color='gray',alpha=0.2)
plt.legend()
plt.show()

# Returns
returns = (pd.Series([(sell-buy)/buy for sell,buy in zip(sellprice,buyprice)])+1).prod()-1
