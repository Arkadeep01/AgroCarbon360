# ml_models/pipelines/train.py
import os
import yaml
import joblib
import json
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

from pipelines.utils import read_any_table, normalize_columns, choose_target, summarize_df
from preprocessing.preprocess import clean_dataset, split_data
from models.random_forest import build_random_forest

def main():
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Load Data
    df = read_any_table(config["data"]["s1_path"], sheet_name=config["data"].get("sheet_name"))
    df = normalize_columns(df)
    summarize_df(df, "Data S1")

    # Pick target
    target = choose_target(df, config["targets"]["field_level_candidates"])
    if not target:
        raise ValueError("No suitable target column found!")

    print(f"✅ Using target: {target}")

    # Preprocess
    df = clean_dataset(df, target)
    X_train, X_test, y_train, y_test, scaler = split_data(
        df, target, config["data"]["test_size"], config["data"]["random_state"]
    )

    # Model
    model = build_random_forest(
        n_estimators=config["training"]["n_estimators"],
        max_depth=config["training"]["max_depth"],
        min_samples_leaf=config["training"]["min_samples_leaf"],
        random_state=config["data"]["random_state"]
    )

    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"📊 Model R² score: {score:.3f}")

    # Save artifacts
    os.makedirs(config["export"]["model_dir"], exist_ok=True)

    joblib.dump(model, os.path.join(config["export"]["model_dir"], config["export"]["pkl_name"]))
    joblib.dump(scaler, os.path.join(config["export"]["model_dir"], "scaler.pkl"))

    # Save ONNX
    initial_type = [("float_input", FloatTensorType([None, X_train.shape[1]]))]
    onnx_model = convert_sklearn(model, initial_types=initial_type)
    with open(os.path.join(config["export"]["model_dir"], config["export"]["onnx_name"]), "wb") as f:
        f.write(onnx_model.SerializeToString())

    # Save feature list
    features = df.drop(columns=[target]).columns.tolist()
    with open(os.path.join(config["export"]["model_dir"], config["export"]["feature_list_name"]), "w") as f:
        json.dump(features, f)

    # Save model card
    with open(os.path.join(config["export"]["model_dir"], config["export"]["model_card"]), "w") as f:
        f.write(f"# CH4 Baseline Model\n\n")
        f.write(f"- Target: {target}\n")
        f.write(f"- Features: {len(features)}\n")
        f.write(f"- R² on test: {score:.3f}\n")

if __name__ == "__main__":
    main()
