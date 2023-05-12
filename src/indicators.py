import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
#from util import get_data
import yfinance as yf


def sma(df, window=20):
    df = df[['Price']]
    sma = df.rolling(window=window).mean()
    sma.columns = ['sma']
    return sma


def bollinger_bands(df, window=20):
    sma_mean = sma(df[['Price']])
    sma_std = df['Price'].rolling(window=window).std()
    upper = sma_mean['sma'] + 2 * sma_std
    lower = sma_mean['sma'] - 2 * sma_std
    return upper, lower


def bollinger_pct(df, df_bb_lower, df_bb_upper):
    bb_pct = ((df['Price'] - df_bb_lower) / (df_bb_upper - df_bb_lower)) 
    #umerator = df[['Price']] - df_bb_lower[['Price']]
    #bb_pct.columns = ['bb']
    return pd.DataFrame(bb_pct, columns=['bb_pct'])


def momentum(df, window=20):
    moment = (df[['Price']]/ df[['Price']].shift(window)) * 100
    moment.columns = ['momentum']
    return moment


def cci(df, window=20):
    df = df.copy()
    df['typical'] = df[['High', 'Low', 'Price']].mean(axis=1)
    df['sma'] = df['Price'].rolling(window).mean()
    df['mad'] = df['Price'].rolling(window).apply(lambda x: np.fabs(x - x.mean()).mean(), raw=False)
    df['cci'] = (df['typical'] - df['sma']) / (0.015 * df['mad'])
    return df[['cci']]


def stochastic_oscillator(df, window=20):
    LN = df[['Price']].rolling(window=window).min()
    HN = df[['Price']].rolling(window=window).max()
    so = (df[['Price']] - LN) / (HN - LN) * 100
    so.columns = ['so']
    return so

def macd(df):
    df_ema_12 = df[['Price']].ewm(span=12).mean()
    df_ema_26 = df[['Price']].ewm(span=26).mean()
    macd = df_ema_12 - df_ema_26
    macd_signal = macd.ewm(span=9).mean()
    macd_signal.columns = ['macd']
    return macd_signal


def get_data(symbol, start_date = '2018-01-01' , end_date = dt.datetime.today(), missing_day=None):
    # returns weekly stock prices    
    df = yf.Ticker(symbol).history(start=start_date, end=end_date)
    df.fillna(method="ffill").fillna(method="bfill", inplace=True)
    df.rename(columns={'Close':'Price'}, inplace=True)
    
    if missing_day is not None:
        df = pd.concat([df, missing_day], axis=0)
        
    return df[['Price', 'Open', 'High', 'Low', 'Volume']]


def get_indicators(symbol="JPM", sd=dt.datetime(2018, 1, 1), ed=dt.datetime(2021, 12, 15), missing_day=None):

    df_data = get_data(symbol, start_date=sd, end_date=ed, missing_day=missing_day)
    df_data = df_data.fillna(method="ffill").fillna(method="bfill")
    #df_prices = df_prices / df_prices[-1]
    df_sma = sma(df_data)
    df_bb_lower, df_bb_upper = bollinger_bands(df_data)
    df_bb_pct = bollinger_pct(df_data, df_bb_lower, df_bb_upper)
    df_momentum = momentum(df_data)
    
    df_cci = cci(df_data)
    
    df_so = stochastic_oscillator(df_data)
    df_macd= macd(df_data)
    df_indicators = pd.concat([df_data[['Price', 'Volume']], df_sma, df_bb_pct, df_momentum, df_cci, df_so, df_macd],axis=1)
    
    return df_indicators

