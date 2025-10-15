from playwright.sync_api import sync_playwright
from datetime import datetime
import time

APP_URL = "https://abtabed.streamlit.app"
RETRIES = 3
WAIT_AFTER_WAKE = 240  # 4 minutes

def ping_streamlit_app():
    print(f"[{datetime.now()}] 🔄 Checking Streamlit app: {APP_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        status = "❓ Unknown status"
        attempt = 0

        while attempt < RETRIES:
            attempt += 1
            print(f"\n--- Attempt {attempt}/{RETRIES} ---")
            page.goto(APP_URL)

            try:
                # Check if app is asleep
                asleep = page.locator("text=Zzz").count() > 0 and page.locator("text='yes, get this app back up'").count() > 0
                if asleep:
                    print("⚠️ App is asleep. Clicking 'Yes, get this app back up'...")
                    page.locator("text='yes, get this app back up'").click()
                    status = "a. App just woke up"
                    print(status)
                    print(f"⏳ Waiting {WAIT_AFTER_WAKE//60} minutes for backend...")
                    time.sleep(WAIT_AFTER_WAKE)

                # Check for elements
                has_info = page.locator("text=info").count() > 0
                has_about_me = page.locator("text='About Me'").count() > 0

                if has_info and has_about_me:
                    if status != "a. App just woke up":
                        status = "b. App already awake"
                    print(f"✅ Elements detected: info={has_info}, About Me={has_about_me}")
                    break  # success, exit retry loop
                else:
                    page_content = page.content().lower()
                    if "zzz" in page_content:
                        status = "d. App waking up"
                    else:
                        status = "c. Only CDN response"
                    print(f"⚠️ Elements not fully detected. Status: {status}")

            except Exception as e:
                print(f"❌ Error during page check: {e}")
                status = "❌ Error"

            if attempt < RETRIES and status not in ["a. App just woke up", "b. App already awake"]:
                print("⏳ Retrying in 15 seconds...")
                time.sleep(15)

        browser.close()
        print(f"\n[{datetime.now()}] Final status after {attempt} attempts: {status}")

if __name__ == "__main__":
    ping_streamlit_app()

# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime

# APP_URL = "https://abtabed.streamlit.app"

# def ping_streamlit():
#     print(f"[{datetime.now()}] 🔄 Pinging {APP_URL} ...")

#     headers = {
#         "User-Agent": "Mozilla/5.0",
#         "Accept": "text/html",
#     }

#     try:
#         resp = requests.get(APP_URL, headers=headers, timeout=20)
#         print(f"HTTP Status: {resp.status_code}")

#         soup = BeautifulSoup(resp.text, "html.parser")
#         # Look for the span that contains "About Me"
#         found = soup.find(lambda tag: tag.name == "span" and "About Me" in tag.text)

#         if found:
#             print("✅ App HTML contains 'About Me' — backend likely awake.")
#         elif "please wait" in resp.text.lower():
#             print("🕐 App is loading or waking up.")
#         else:
#             print("⚠️ Unexpected response. Might be CDN cache only.")

#     except Exception as e:
#         print(f"❌ Error: {e}")


# if __name__ == "__main__":
#     import time
#     for i in range(3):
#         print(f"\nAttempt {i+1}/3")
#         ping_streamlit()
#         time.sleep(5)