import requests
from datetime import datetime

def ping_streamlit():
    url = "https://abtabed.streamlit.app"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    session = requests.Session()
    try:
        print(f"[{datetime.now()}] 🔄 Pinging {url} ...")
        response = session.get(url, headers=headers, allow_redirects=True, timeout=20)
        print(f"Final URL: {response.url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print("Success" if response.status_code == 200 else "Failed")
        # Check for login keyword
        if "Sign in" in response.text or "streamlitLogin" in response.text:
            print("⚠️  WARNING: App might be private or redirected to login.")
        elif "streamlit" in response.text.lower():
            print("✅ App is up and responding correctly.")
        else:
            print("❓ Unexpected response content. App may be loading or unstable.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ping_streamlit()