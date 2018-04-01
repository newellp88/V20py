"""
A momentum strategy using Bollinger Bands and a Stochastic Oscillator to
generate singals.
"""
import numpy as np
import pandas as pd
from indicators import Indicators
import matplotlib.pyplot as plt

# import and clean data
f = r'data/AUD_JPY_H1_history.csv'
df = pd.read_csv(f)
df.drop("Unnamed: 0", axis=1, inplace=True)
filename = f[5:-4]

# add the technical indicators to the dataframe
technical = Indicators()
df = technical.stoch(df, 14, 7)
df = technical.bollBands(df, 10, 2)

# graph the results
fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(30,20))
df[['Close','Rolling Mean','Bollinger High','Bollinger Low']].plot(ax=axes[0]).set_title("Close and Bollinger")
df[['%K','%D']].plot(ax=axes[1]).set_title("Stochastic")
plt.savefig('examples/stoch-bands-%s.png' % filename)

# add long/short signals to the dataframe
df['Enter Short'] = ((df['%K']<df['%D'])&(df['%K'].shift(1) > df['%D'].shift(1))) & (df['%D']>80) & (df['Close'] < df['Rolling Mean'])
df['Enter Long'] = ((df['%K']>df['%D']) & (df['%K'].shift(1) < df['%D'].shift(1))) & (df['%D'] < 20) & (df['Close'] > df['Rolling Mean'])
df['Position'] = np.nan
df.loc[df['Enter Short'],'Position'] = -1
df.loc[df['Enter Long'], 'Position'] = 1
df['Position'].iloc[0] = 0
df['Position'] = df['Position'].fillna(method='ffill')

# compare strategy to raw returns of the asset
df['Asset Returns'] = df['Close'].pct_change()
df['Strategy Returns'] = df['Asset Returns'] * df['Position'].shift(1)
df[['Strategy Returns','Asset Returns']].cumsum().plot().set_title("Strategy vs Asset Returns")
plt.savefig('examples/stoch-bands-returns-%s.png' % filename)

"""

"""
