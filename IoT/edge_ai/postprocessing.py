"""
postprocessing.py
Map raw model outputs (probabilities, regression numbers) to actionable text or structured actions.
Keep logic simple and deterministic so that on-device advice is clear.
"""

import numpy as np

CROP_LABELS = {
    0: "rice",
    1: "wheat",
    2: "maize",
    3: "pulse",
    4: "millets"
}

def parse_crop_reco(output_array):
    """
    Parse the output array from the crop recommendation model to get the recommended crop.
    
    Args:
        output_array (np.ndarray): The raw output array from the model, expected shape (5,).
        
    Returns:
        str: The recommended crop label.
    """
    probs = np.squeeze(output_array)
    if probs.sum() <= 1.0 + 1e-6:
        p = probs
    else:
        exps = np.exp(probs - np.max(probs))
        p = exps / np.sum(exps)
    mapping = {CROP_LABELS[i]: float(p[i]) for i in range(min(len(p), len(CROP_LABELS)))}
    top = max(mapping.items(), key=lambda x: x[1])
    return mapping, {"recommended_crop": top[0], "confidence": top[1]}

def parse_irrigation(output_array):
    """
    output_array: could be a regression output (e.g., recommended mm of water) or classification.
    For this example, assume output_array is [days_until_irrigation, liters_per_hectare]
    """
    arr = np.squeeze(output_array)
    if arr.size == 1:
        # single regression value -> interpret as days
        days = float(arr[0])
        return {"days_until_irrigation": max(0, round(days))}
    elif arr.size >= 2:
        days = int(round(arr[0]))
        liters = float(arr[1])
        return {"days_until_irrigation": max(0, days), "liters_per_hectare": max(0.0, liters)}
    else:
        return {"message": "no irrigation recommendation"}

def parse_anomaly(output_array, threshold=0.5):
    """
    output_array: probability of anomaly [0..1].
    returns True if anomaly.
    """
    score = float(np.squeeze(output_array))
    return {"anomaly_score": score, "is_anomaly": score >= threshold}

# utility to create final user-friendly message
def generate_user_advice(crop_info, irr_info, anomaly_info):
    messages = []
    if anomaly_info.get("is_anomaly"):
        messages.append(f"Sensor anomaly detected (score {anomaly_info['anomaly_score']:.2f}). Please check sensor & wiring.")
    if crop_info:
        messages.append(f"Recommended crop: {crop_info['recommended_crop']} (confidence {crop_info['confidence']:.2f})")
    if irr_info:
        if "days_until_irrigation" in irr_info:
            messages.append(f"Next irrigation in {irr_info['days_until_irrigation']} day(s).")
        if "liters_per_hectare" in irr_info:
            messages.append(f"Apply ~{irr_info['liters_per_hectare']:.0f} L/ha when irrigating.")
    return {"messages": messages, "summary": " ".join(messages)}

if __name__ == "__main__":
    # test mocks
    crop_probs = np.array([[0.1, 0.2, 0.6, 0.05, 0.05]])
    irr = np.array([[3.0, 250.0]])
    anomaly = np.array([[0.12]])
    mapping, crop_info = parse_crop_reco(crop_probs)
    irr_info = parse_irrigation(irr)
    anomaly_info = parse_anomaly(anomaly)
    print(generate_user_advice(crop_info, irr_info, anomaly_info))