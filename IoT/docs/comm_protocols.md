1. MQTT topic hierarchy (e.g., iot/farm/{device_id}/sensor_data).
2. LoRaWAN payload format with byte-level encoding for sensor readings.
3. GSM/HTTP fallback data packet format (JSON schema).
4. Security layers (TLS, AES keys, device authentication tokens).
5. Retry and backoff strategy in case of connectivity loss.


Examples of payloads:

{
  "device_id": "ESP32_001",
  "timestamp": "2025-09-01T12:30:00Z",
  "soil_moisture": 28.3,
  "temperature": 31.5,
  "ph": 6.7
}