"""
Moving average cross strategy.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from indicators import Indicators

# import and clean data
f = r'data/USD_CAD_H1_history.csv'
df = pd.read_csv(f)
df.drop("Unnamed: 0", axis=1, inplace=True)
filename = f[5:-4]

# add moving averages
technical = Indicators()
df['fast sma'] = technical.sma1(df['Close'], 7)
df['slow sma'] = technical.sma1(df['Close'], 20)

# graph the results
df[['Close','fast sma', 'slow sma']].plot(figsize=(30,20)).set_title("Moving Average Cross")
plt.savefig('examples/max-%s.png' % filename)

# set strategy
df['Enter Short'] = (df['fast sma'].shift(1) < df['slow sma'])
df['Enter Long'] = (df['fast sma'].shift(1) > df['slow sma'])
df['Position'] = np.nan
df.loc[df['Enter Short'],'Position'] = -1
df.loc[df['Enter Long'], 'Position'] = 1
df['Position'].loc[0] = 0
df['Position'] = df['Position'].fillna(method='ffill')

# compare strategy and asset returns
df['Asset Returns'] = df['Close'].pct_change()
df['Strategy Returns'] = df['Asset Returns'] * df['Position'].shift(1)
df[['Strategy Returns','Asset Returns']].cumsum().plot().set_title("Strategy vs Asset Returns")
plt.savefig('examples/max-strategy-returns-%s.png' % filename)
