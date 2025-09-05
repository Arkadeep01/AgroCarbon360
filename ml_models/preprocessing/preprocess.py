# ml_models/preprocessing/preprocess.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def clean_dataset(df: pd.DataFrame, target: str):
    """
    Basic preprocessing: drops NA in target, fills numeric NA with median.
    """
    df = df.copy()
    df = df.dropna(subset=[target])

    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())

    return df

def split_data(df: pd.DataFrame, target: str, test_size=0.2, random_state=42):
    """
    Splits dataset into train/test with scaling.
    """
    X = df.drop(columns=[target])
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler
