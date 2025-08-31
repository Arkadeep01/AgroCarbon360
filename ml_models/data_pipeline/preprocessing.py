import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

class DataPreprocessor:
    def __init__(self, scaling_method="standard"):
        self.scaler = StandardScaler() if scaling_method == "standard" else MinMaxScaler()
        self.encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        self.imputer = SimpleImputer(strategy="mean")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates, handle missing values, standardize column names"""
        df = df.drop_duplicates()
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        return df

    def handle_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values with mean for numerical and mode for categorical"""
        num_cols = df.select_dtypes(include=np.number).columns
        cat_cols = df.select_dtypes(exclude=np.number).columns
        
        df[num_cols] = self.imputer.fit_transform(df[num_cols])
        for col in cat_cols:
            df[col] = df[col].fillna(df[col].mode()[0])
        return df

    def encode_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """One-hot encode categorical variables"""
        cat_cols = df.select_dtypes(exclude=np.number).columns
        if len(cat_cols) > 0:
            encoded = pd.DataFrame(self.encoder.fit_transform(df[cat_cols]), columns=self.encoder.get_feature_names_out(cat_cols))
            df = pd.concat([df.drop(columns=cat_cols), encoded], axis=1)
        return df

    def scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        num_cols = df.select_dtypes(include=np.number).columns
        df[num_cols] = self.scaler.fit_transform(df[num_cols])
        return df

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete pipeline: clean → missing → encode → scale"""
        df = self.clean_data(df)
        df = self.handle_missing(df)
        df = self.encode_features(df)
        df = self.scale_features(df)
        return df
