"""
inference.py
Edge inference runner for Raspberry Pi / edge gateway using TensorFlow Lite.

Features:
- Load multiple TFLite models (crop_reco, irrigation, anomaly)
- Preprocess sensor JSON -> feature vector
- Run each model and postprocess outputs into user-friendly advice
- Safe model interpreter creation with fallback between tflite-runtime and tensorflow.lite

Usage:
    python inference.py --model-dir ./models --input sample.json
"""

import os
import argparse
import json
import numpy as np
from time import time

# Try to import tflite-runtime first (lightweight), else fallback to tensorflow
try:
    from tflite_runtime.interpreter import Interpreter
    from tflite_runtime.interpreter import load_delegate
    TFLITE_IMPL = "tflite-runtime"
except Exception:
    try:
        from tensorflow.lite.python.interpreter import Interpreter
        TFLITE_IMPL = "tensorflow"
    except Exception:
        raise RuntimeError("No TFLite runtime found. Install 'tflite-runtime' or 'tensorflow'.")

from preprocessing import build_feature_vector
from postprocessing import parse_crop_reco, parse_irrigation, parse_anomaly, generate_user_advice

MODEL_FILENAMES = {
    "crop": "crop_reco_model.tflite",
    "irrigation": "irrigation_advice.tflite",
    "anomaly": "anomaly_detect.tflite"
}

def load_tflite_model(path):
    """Create and return a TFLite interpreter"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    interpreter = Interpreter(model_path=path)
    interpreter.allocate_tensors()
    return interpreter

def run_interpreter(interpreter, input_data):
    """Run interpreter (single input sample) and return output arrays (list)"""
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    # assume single input tensor
    interpreter.set_tensor(input_details[0]['index'], input_data)
    start = time()
    interpreter.invoke()
    duration = time() - start
    outputs = []
    for od in output_details:
        out = interpreter.get_tensor(od['index'])
        outputs.append(out)
    return outputs, duration

def predict_all(model_dir, sensor_payload, feature_order=None):
    # Build feature vector
    x = build_feature_vector(sensor_payload, feature_order=feature_order)  # shape (1, N)
    results = {}
    times = {}

    # Crop
    crop_path = os.path.join(model_dir, MODEL_FILENAMES["crop"])
    crop_interpreter = load_tflite_model(crop_path)
    outs, t = run_interpreter(crop_interpreter, x)
    times['crop_ms'] = t * 1000
    mapping, crop_info = parse_crop_reco(outs[0])
    results['crop'] = {"mapping": mapping, "info": crop_info}

    # Irrigation - assume same features or a different feature vector; if different, compute accordingly
    irr_path = os.path.join(model_dir, MODEL_FILENAMES["irrigation"])
    irr_interpreter = load_tflite_model(irr_path)
    outs, t = run_interpreter(irr_interpreter, x)
    times['irrigation_ms'] = t * 1000
    irr_info = parse_irrigation(outs[0])
    results['irrigation'] = irr_info

    # Anomaly detection
    anom_path = os.path.join(model_dir, MODEL_FILENAMES["anomaly"])
    anom_interpreter = load_tflite_model(anom_path)
    outs, t = run_interpreter(anom_interpreter, x)
    times['anomaly_ms'] = t * 1000
    anom_info = parse_anomaly(outs[0])
    results['anomaly'] = anom_info

    # Combined user-friendly advice
    advice = generate_user_advice(results['crop']['info'], results['irrigation'], results['anomaly'])
    return {"results": results, "advice": advice, "times": times}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", default="./models", help="Folder containing .tflite models")
    parser.add_argument("--input", default=None, help="JSON file with sensor readings")
    args = parser.parse_args()

    if args.input:
        payload = json.load(open(args.input))
    else:
        # quick sample if no input provided
        payload = {
            "soil_moisture": 35.0,
            "soil_ph": 6.4,
            "soil_temp_c": 28.0,
            "air_temp_c": 30.0,
            "rain_last_7d_mm": 45.0,
            "ec": 1.2
        }

    out = predict_all(args.model_dir, payload,
                      feature_order=["soil_moisture","soil_ph","soil_temp_c","air_temp_c","rain_last_7d_mm","ec"])
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
