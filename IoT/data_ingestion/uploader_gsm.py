# uploader_gsm.py
import requests
import json
from payload_formatter import format_payload

API_URL = "https://backend.example.com/api/iot/data"

def upload_gsm(data):
    payload = format_payload(data, source="gsm")
    resp = requests.post(API_URL, json=payload)
    print("Upload status:", resp.status_code)
