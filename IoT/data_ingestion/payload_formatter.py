# payload_formatter.py
import json, time

def format_payload(raw, source="unknown"):
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except:
        data = {"raw": raw}

    return {
        "device_id": data.get("device_id", "unknown"),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "data": data
    }
