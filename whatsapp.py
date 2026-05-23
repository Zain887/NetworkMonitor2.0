import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import PROFILE_DIR
from logger import logger

class WhatsAppSender:
    def __init__(self):
        logger.log("Starting WhatsApp Web with Persistent Profile...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-data-dir={PROFILE_DIR}")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://web.whatsapp.com")
        self._authenticate()

    def _authenticate(self):
        try:
            logger.log("Checking if session is already authenticated...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='pane-side']"))
            )
            logger.success("Authenticated automatically via cached user session data!")
        except Exception:
            logger.warn("Authentication token missing or expired.")
            input("👉 Please scan the QR code displayed on screen, wait for chats to load, then press ENTER here...")

    @staticmethod
    def clean_phone_number(phone_raw):
        if pd.isna(phone_raw) or not phone_raw:
            return None
        if isinstance(phone_raw, float):
            phone_raw = int(phone_raw)
        phone_str = str(phone_raw).strip()
        return "".join(c for c in phone_str if c.isdigit())

    def dispatch_alert(self, alert_item):
        name = alert_item["name"]
        ip = alert_item["ip"]
        status = alert_item["status"]
        phone = self.clean_phone_number(alert_item["phone"])

        if not phone:
            logger.error(f"Missing or corrupt phone data for {name}. Alert aborted.")
            return

        try:
            msg = f"*{status}*\n\nDevice: {name}\nIP: {ip}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            chat_url = f"https://web.whatsapp.com/send?phone={phone}"
            logger.log(f"Opening chat payload viewport for {name} ({phone})...")
            self.driver.get(chat_url)

            box = None
            xpaths_to_try = [
                "//footer//div[@contenteditable='true']",
                "//div[@contenteditable='true'][@aria-label='Type a message']",
                "//div[@contenteditable='true'][@data-tab='10']",
                "//div[@role='textbox']"
            ]
            
            for path in xpaths_to_try:
                try:
                    box = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, path))
                    )
                    if box:
                        break
                except Exception:
                    continue
            
            if box is None:
                raise Exception("WhatsApp Web structure layout mismatch. Textbox unreachable.")

            box.click()
            time.sleep(0.5)

            # Execution block mapping string parameters using ClipboardEvents data
            script = """
            const dataTransfer = new DataTransfer();
            dataTransfer.setData('text/plain', arguments[0]);
            const event = new ClipboardEvent('paste', { clipboardData: dataTransfer, bubbles: true });
            arguments[1].dispatchEvent(event);
            """
            self.driver.execute_script(script, msg, box)
            
            time.sleep(1)
            box.send_keys(Keys.ENTER)
            time.sleep(3.0)
            logger.success(f"Alert successfully pushed to {phone}")
            
        except Exception as e:
            logger.error(f"WhatsApp Delivery Failed for {name}: {e}")

    def close(self):
        try:
            self.driver.quit()
            logger.success("Chrome session killed safely.")
        except Exception:
            pass