#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 12:31:04 2022
@author: troysattgast
@todo:  functionalize
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

############################################################
#Find the difference between stock price and strike price
#Multiply the result by open interest at that strike
#Add together the dollar value for the put and call at that strike

#Repeat for each strike price
#Find the highest value strike price. This price is equivalent to max pain price.


stock = 'IWM'
tk = yf.Ticker(stock)  
exps = tk.options  #expiration dates
print(exps)
expiry = exps[1]
options = tk.option_chain(expiry)
options.calls['type'] = 'call'
options.puts['type'] = 'put'


calls = options.calls
puts = options.puts
calls.columns = [col+'_call' for col in calls.columns]
puts.columns = [col+'_put' for col in puts.columns]


df = calls.merge(puts, left_on='strike_call', right_on='strike_put', how='outer', validate='one_to_one', indicator=True)

df['strike'] = np.where(df['strike_call'].isnull(), df['strike_put'], df['strike_call'])
df.sort_values(by='strike', inplace=True)
#plt.plot(df['strike'], df[['openInterest_call', 'openInterest_put']])


df['call_pain'] = (abs(tk.info['regularMarketPrice'] - df['strike'] )) * df['openInterest_call'] 
df['put_pain'] = (abs(tk.info['regularMarketPrice'] - df['strike'] )) * df['openInterest_put']
df['call_pain'].fillna(0, inplace=True)
df['put_pain'].fillna(0, inplace=True)
df['call_sum'] = df['call_pain'].cumsum()
df['put_sum'] = df['put_pain'][::-1].cumsum()
df['cross'] = np.where(df['call_sum'] > df['put_sum'], 1, 0)
df['max_pain'] = abs(df['call_sum'] + df['put_sum'])
max_pain = df.loc[df['max_pain'] == df['max_pain'].min()]
plt.plot(df['strike'], df[['call_sum', 'put_sum']])
plt.title(f'''Max pain at ${max_pain["strike"].values[0]} for {stock} expiring on {expiry} \n
          Current price:  ${tk.info["regularMarketPrice"]} ''')


plt.title(f'Open Interest for {stock} expiring on {expiry}')
plt.plot(df['strike'], df[['openInterest_call', 'openInterest_put']])




fig, ax = plt.subplots()
ax.plot(df['strike'], df[['call_sum', 'put_sum']])

# Use automatic StrMethodFormatter
ax.yaxis.set_major_formatter('{x:,.0f}')    
ax.xaxis.set_major_formatter('${x:,.0f}')


#ax.yaxis.set_tick_params(which='major', labelcolor='green',
#                         labelleft=False, labelright=True)



plt.show()


