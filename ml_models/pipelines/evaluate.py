# ml_models/pipelines/evaluate.py
import os
import yaml
import joblib
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from pipelines.utils import read_any_table, normalize_columns, choose_target
from preprocessing.preprocess import clean_dataset, split_data

def main():
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Load dataset
    df = read_any_table(config["data"]["s1_path"], sheet_name=config["data"]["sheet_name"])
    df = normalize_columns(df)

    target = choose_target(df, config["targets"]["field_level_candidates"])
    if not target:
        raise ValueError("No target found in dataset!")

    df = clean_dataset(df, target)
    X_train, X_test, y_train, y_test, scaler = split_data(
        df, target, config["data"]["test_size"], config["data"]["random_state"]
    )

    # Load artifacts
    model_path = os.path.join(config["export"]["model_dir"], config["export"]["pkl_name"])
    model = joblib.load(model_path)

    # Predictions
    y_pred = model.predict(X_test)

    # Metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n📊 Evaluation Results")
    print(f"R² Score: {r2:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"RMSE: {rmse:.3f}")

    # Plot: Predicted vs Actual
    plt.figure(figsize=(6, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--")
    plt.xlabel("Actual CH₄")
    plt.ylabel("Predicted CH₄")
    plt.title("Predicted vs Actual Methane Emissions")
    plt.savefig(os.path.join(config["export"]["model_dir"], "pred_vs_actual.png"))
    plt.close()

    # Plot: Error distribution
    errors = y_test - y_pred
    plt.figure(figsize=(6, 4))
    plt.hist(errors, bins=30, edgecolor="black", alpha=0.7)
    plt.xlabel("Prediction Error")
    plt.ylabel("Frequency")
    plt.title("Error Distribution")
    plt.savefig(os.path.join(config["export"]["model_dir"], "error_distribution.png"))
    plt.close()

    # Plot: Feature Importance
    features = df.drop(columns=[target]).columns.tolist()
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(8, 6))
    plt.bar(range(len(features)), importances[indices], align="center")
    plt.xticks(range(len(features)), np.array(features)[indices], rotation=45, ha="right")
    plt.title("Feature Importance (Random Forest)")
    plt.tight_layout()
    plt.savefig(os.path.join(config["export"]["model_dir"], "feature_importance.png"))
    plt.close()

    print("✅ Plots saved in:", config["export"]["model_dir"])

if __name__ == "__main__":
    main()
