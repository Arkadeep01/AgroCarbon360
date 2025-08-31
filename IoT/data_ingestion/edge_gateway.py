# edge_gateway.py
import time, json, sqlite3, requests
from payload_formatter import format_payload

API_URL = "https://backend.example.com/api/iot/data"
DB_FILE = "cache.db"

# Local cache init
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS cache (id INTEGER PRIMARY KEY, payload TEXT)")
conn.commit()

def forward_payload(payload):
    try:
        resp = requests.post(API_URL, json=payload, timeout=5)
        if resp.status_code == 200:
            print("Uploaded:", payload)
            return True
    except Exception as e:
        print("Offline, caching:", e)
    return False

def cache_payload(payload):
    cur.execute("INSERT INTO cache (payload) VALUES (?)", [json.dumps(payload)])
    conn.commit()

def flush_cache():
    cur.execute("SELECT * FROM cache")
    rows = cur.fetchall()
    for r in rows:
        pid, pjson = r
        payload = json.loads(pjson)
        if forward_payload(payload):
            cur.execute("DELETE FROM cache WHERE id=?", [pid])
            conn.commit()

while True:
    # simulate reading payload
    payload = format_payload({"temperature": 25}, source="gateway")
    if not forward_payload(payload):
        cache_payload(payload)
    flush_cache()
    time.sleep(10)
