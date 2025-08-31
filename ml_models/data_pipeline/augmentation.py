import pandas as pd
import numpy as np

def add_noise(df: pd.DataFrame, noise_level=0.01):
    """Adds Gaussian noise to numerical features"""
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        df[col] += np.random.normal(0, noise_level, size=df[col].shape)
    return df
