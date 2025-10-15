import requests
import websocket
from urllib.parse import urlparse
from datetime import datetime

APP_URL = "https://abtabed.streamlit.app"

def ping_streamlit():
    print(f"[{datetime.now()}] 🔄 Pinging {APP_URL} ...")

    # Step 1. Send normal HTTP GET
    try:
        response = requests.get(APP_URL, timeout=15)
        print(f"HTTP Status: {response.status_code}")
        if response.status_code != 200:
            print("❌ App unreachable.")
            return
        print("🌐 Frontend reachable.")
    except Exception as e:
        print(f"❌ HTTP request failed: {e}")
        return

    # Step 2. Extract correct host for WebSocket
    parsed = urlparse(APP_URL)
    host = parsed.netloc
    ws_url = f"wss://{host}/_stcore/stream"

    print(f"Attempting WebSocket handshake with: {ws_url}")

    try:
        ws = websocket.create_connection(ws_url, timeout=10)
        print("✅ WebSocket handshake successful — backend container is awake.")
        ws.close()
    except Exception as e:
        print(f"⚠️ WebSocket connection failed: {e}")

if __name__ == "__main__":
    import time

    for i in range(3):
        print(f"\nAttempt {i+1}/3")
        ping_streamlit()
        time.sleep(5)