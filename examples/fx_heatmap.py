"""
Generate a heatmap to visualize fx correlations.
"""
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def createMetaFrame(window):
    meta_df = pd.DataFrame()
    folder = 'data/'
    for files in os.walk(folder):
        for f in files[2]:
            time_period = f[8:11]
            if window == time_period:
                instr = f[0:7]
                target = os.path.join(folder, f)
                df = pd.read_csv(target)
                close = df['Close']
                meta_df[instr] = close
    return meta_df

def correlationHeatMap(df):
    corr_df = df.corr()
    ax = sns.heatmap(corr_df, annot=True)
    plt.savefig('examples/fx_correlation_heatmap.png')
    plt.show()

meta = createMetaFrame('M15')
correlationHeatMap(meta)
