from sklearn.model_selection import train_test_split
import pandas as pd

def split_dataset(df: pd.DataFrame, target_column: str, test_size=0.2, val_size=0.1, random_state=42):
    """Splits dataset into train, validation, and test sets"""
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_state)
    train_df, val_df = train_test_split(train_df, test_size=val_size, random_state=random_state)
    
    X_train = train_df.drop(columns=[target_column])
    y_train = train_df[target_column]

    X_val = val_df.drop(columns=[target_column])
    y_val = val_df[target_column]

    X_test = test_df.drop(columns=[target_column])
    y_test = test_df[target_column]

    return X_train, y_train, X_val, y_val, X_test, y_test
