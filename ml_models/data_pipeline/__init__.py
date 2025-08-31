import pandas as pd
from ml_models.data_pipeline.preprocessing import DataPreprocessor
from ml_models.data_pipeline.split_data import split_dataset

# Load your dataset
df = pd.read_csv("data/farm_data.csv")

# Initialize Preprocessor
preprocessor = DataPreprocessor(scaling_method="standard")
processed_df = preprocessor.preprocess(df)

# Split into train/val/test
X_train, y_train, X_val, y_val, X_test, y_test = split_dataset(processed_df, target_column="carbon_credits")
