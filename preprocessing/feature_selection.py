import pandas as pd
import numpy as np

def remove_highly_correlated_features(df, threshold=0.9):

    corr = df.corr().abs()

    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))

    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]

    df = df.drop(columns=to_drop)

    return df, to_drop