# uploader_wifi.py
import asyncio
import websockets
import json
from payload_formatter import format_payload

async def listen():
    uri = "ws://backend.example.com/ws/iot"
    async with websockets.connect(uri) as ws:
        while True:
            raw = await ws.recv()
            payload = format_payload(raw, source="wifi")
            print("Received via WiFi:", payload)

asyncio.run(listen())
