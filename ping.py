import requests
import websocket
import time
from datetime import datetime

APP_URL = "https://abtabed.streamlit.app"

def ping_streamlit():
    print(f"[{datetime.now()}] Pinging {APP_URL}")
    response = requests.get(APP_URL, timeout=15)
    if response.status_code == 200:
        print("🌐 Frontend reachable.")
    else:
        print("❌ HTTP failed.")
        return

    # Extract app host (for websocket)
    host = APP_URL.replace("https://", "").replace("http://", "")
    ws_url = f"wss://{host}/_stcore/stream"

    try:
        print(f"🔌 Connecting to WebSocket: {ws_url}")
        ws = websocket.create_connection(ws_url, timeout=10)
        print("✅ WebSocket handshake OK — backend container woke up.")
        ws.close()
    except Exception as e:
        print(f"⚠️ WebSocket connection failed: {e}")

if __name__ == "__main__":
    ping_streamlit()