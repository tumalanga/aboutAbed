import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


TARGET_URL = "https://abtabed.streamlit.app/"
SLEEP_KEYWORD = "This app has gone to sleep due to inactivity. Would you like to wake it back up?"


def ping():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Uncomment untuk mode headless (tanpa tampilan browser):
    options.add_argument("--headless")

    print("🚀 Membuka browser...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # Step 1: Akses URL target
        print(f"🌐 Mengakses {TARGET_URL}...")
        driver.get(TARGET_URL)

        print("⏳ Menunggu 10 detik...")
        time.sleep(10)

        # Step 2: Cek apakah app sedang tidur
        page_source = driver.page_source

        if SLEEP_KEYWORD not in page_source:
            print("❌ tidak ditemukan")
            f_body_text = driver.find_element(By.TAG_NAME, "body").text.strip()
            f_words = f_body_text.split()
            f_first_word = f_words[0] if f_words else "(kosong)"

            print(f"\n📄 Cuplikan teks halaman : {f_body_text[:200]}...")
            print(f"🏆 Kata pertama           : {f_first_word}")
            return

        print("✅ App sedang tidur, ditemukan pesan wakeup!")
        print("🖱️  Mencari tombol wakeup...")

        # Coba cari tombol via data-testid dulu, fallback ke teks tombol
        try:
            wakeup_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-testid="wakeup-button-viewer"]')
                )
            )
        except Exception:
            print("⚠️  data-testid tidak ditemukan, mencari via teks tombol...")
            wakeup_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(., "Yes, get this app back up")]')
                )
            )

        wakeup_btn.click()
        print("✅ Tombol wakeup berhasil diklik!")

        # Step 3: Tunggu ~1 menit agar app menyala kembali
        print("⏳ Menunggu 60 detik agar app kembali aktif...")
        for i in range(60, 0, -10):
            print(f"   ... {i} detik lagi")
            time.sleep(10)
        print("✅ Selesai menunggu!")

        # Step 4: Scrape kata pertama yang muncul di halaman
        # Ambil semua teks yang terlihat, ambil kata paling pertama
        body_text = driver.find_element(By.TAG_NAME, "body").text.strip()
        words = body_text.split()
        first_word = words[0] if words else "(kosong)"

        print(f"\n📄 Cuplikan teks halaman : {body_text[:200]}...")
        print(f"🏆 Kata pertama           : {first_word}")

    except Exception as e:
        print(f"⚠️  Terjadi error: {e}")

    finally:
        print("\n🛑 Menutup browser & menghentikan program.")
        driver.quit()


if __name__ == "__main__":
    ping()