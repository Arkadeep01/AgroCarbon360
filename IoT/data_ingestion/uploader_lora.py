# uploader_lora.py
import paho.mqtt.client as mqtt
import json
from payload_formatter import format_payload

BROKER = "mqtt.example.com"
TOPIC = "iot/lora"

def on_message(client, userdata, msg):
    raw = msg.payload.decode()
    payload = format_payload(raw, source="lora")
    print("Formatted Payload:", payload)
    # TODO: Forward payload to backend

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC)
client.loop_forever()
