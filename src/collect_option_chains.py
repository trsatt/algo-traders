#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 21:14:33 2022

@author: troysattgast
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime


stocks =['IWM', 'SPY', 'SNAP', 'SLV', 'QQQ', 'XLF', 'XLE']
options = pd.DataFrame()
today = datetime.date.today().strftime('%Y-%m-%d')

for x in stocks:
    print(x)
    tk = yf.Ticker(x)  
    exps = tk.options  #expiration dates
    try:
        for e in exps:
            print(e)
            opt = tk.option_chain(e)
            opt = pd.DataFrame().append(opt.calls).append(opt.puts)
            opt['expirationDate'] = e
            opt['Symbol'] = x
            options = options.append(opt, ignore_index=True)
            options['as_of'] = today
    except:
        pass


options.to_csv('option_prices.csv', mode='a', header=False, index=False)

