"""
preprocessing.py
Standardize and prepare raw sensor readings into model-ready numpy arrays.
Adapt normalization values (means/stds or min/max) per your trained model.
"""

import numpy as np

# Example normalization values (update these based on your training data)
NORMALIZATION_CONFIG = {
    "soil_moisture": {"min": 0.0, "max": 100.0},
    "soil_ph": {"min": 3.0, "max": 9.0},
    "soil_temp_c": {"min": -5.0, "max": 50.0},
    "air_temp_c": {"min": -10.0, "max": 55.0},
    "rain_last_7d_mm": {"min": 0.0, "max": 500.0},
    "ec": {"min": 0.0, "max": 10.0},
}

def clip_and_scale(value, min_val, max_val):
    """Clip the value to [min_val, max_val] and scale to [0, 1]."""
    clipped = np.clip(value, min_val, max_val)
    scaled = (clipped - min_val) / (max_val - min_val)
    return scaled

def normalize_feature(name, value):
    """Normalize a single feature based on predefined min/max values."""
    if name in NORMALIZATION_CONFIG:
        config = NORMALIZATION_CONFIG[name]
        return clip_and_scale(value, config["min"], config["max"])
    else:
        raise ValueError(f"Normalization config for {name} not found.")
    
def build_feature_vector(sensor_data):
    """
    Convert raw sensor data dictionary into a normalized numpy array.
    
    Args:
        sensor_data (dict): Dictionary with keys as feature names and values as raw readings.
        
    Returns:
        np.ndarray: Normalized feature vector ready for model input.
    """
    features = []
    for feature_name in NORMALIZATION_CONFIG.keys():
        if feature_name in sensor_data:
            normalized_value = normalize_feature(feature_name, sensor_data[feature_name])
            features.append(normalized_value)
        else:
            raise ValueError(f"Missing feature {feature_name} in sensor data.")
    
    return np.array(features, dtype=np.float32)


if __name__ == "__main__":
    # Example usage
    raw_sensor_data = {
        "soil_moisture": 45.0,
        "soil_ph": 6.5,
        "soil_temp_c": 22.0,
        "air_temp_c": 18.0,
        "rain_last_7d_mm": 120.0,
        "ec": 2.5,
    }
    
    feature_vector = build_feature_vector(raw_sensor_data)
    print("Normalized Feature Vector:", feature_vector)