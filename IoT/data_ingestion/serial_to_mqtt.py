# serial_to_mqtt.py
import serial, json, paho.mqtt.client as mqtt
from payload_formatter import format_payload

ser = serial.Serial('/dev/ttyUSB0', 9600)
client = mqtt.Client()
client.connect("mqtt.example.com", 1883, 60)

while True:
    raw = ser.readline().decode().strip()
    payload = format_payload(raw, source="serial")
    client.publish("iot/serial", json.dumps(payload))
    print("Sent:", payload)
