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

    def _attempt_delivery(self, phone, msg):
        """Internal helper to process a single delivery attempt using stable JS Event injection."""
        chat_url = f"https://web.whatsapp.com/send?phone={phone}"
        self.driver.get(chat_url)

        # 1. Handle overlay popups or modal blocking alerts
        try:
            ok_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][span[contains(.,'OK')]]"))
            )
            ok_button.click()
            time.sleep(1.5)
            self.driver.get(chat_url)
        except Exception:
            pass 

        # 2. Dynamic Wait: Ensure the core chat app wrapper structure is loaded
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='main'] | //footer"))
            )
        except Exception:
            raise Exception("WhatsApp workspace failed to load in time.")

        # 3. Pure JavaScript injection targeting the text box and handling state
        js_send_script = """
        const msgText = arguments[0];
        
        // Target text boxes using true CSS queries
        const editableBox = document.querySelector('footer div[contenteditable="true"]') || 
                            document.querySelector('div[class*="lexical-rich-text-input"] div[contenteditable="true"]') ||
                            document.querySelector('div[role="textbox"]');
        
        if (!editableBox) return "TEXTBOX_NOT_FOUND";

        // Ensure paragraph node targets exist
        let internalPara = editableBox.querySelector('p');
        if (!internalPara) {
            internalPara = document.createElement('p');
            editableBox.appendChild(internalPara);
        }

        internalPara.innerText = msgText;

        // Dispatches structural UI event chains so react logs the typing action
        const trackingEvent = new InputEvent('input', {
            bubbles: true,
            cancelable: true,
            inputType: 'insertText',
            data: msgText
        });
        internalPara.dispatchEvent(trackingEvent);
        
        return "TEXT_INSERTED";
        """

        # Step 1: Insert the text via JS
        result = self.driver.execute_script(js_send_script, msg)
        if result == "TEXTBOX_NOT_FOUND":
            raise Exception("WhatsApp Web structure layout mismatch. Textbox unreachable.")
            
        time.sleep(1.5) # Give WhatsApp's React state engine time to generate the send button

        # Step 2: Native JavaScript click routine to bypass overlay intersections
        js_click_button = """
        const sendBtn = document.querySelector('span[data-icon="send"]') || 
                        document.querySelector('button span[data-icon="send"]')?.parentElement ||
                        document.querySelector('[data-testid="send"]') ||
                        document.querySelector('button[data-tab="11"]');
        
        if (sendBtn) {
            sendBtn.click(); // Native DOM execution bypasses click interception
            return true;
        }
        return false;
        """

        try:
            button_clicked = self.driver.execute_script(js_click_button)
            if button_clicked:
                logger.success("Send button clicked natively via JavaScript!")
            else:
                raise Exception("Send button could not be located in the DOM tree.")
                
        except Exception as e:
            raise Exception(f"Failed to trigger send button: {e}")
            
        time.sleep(4.0) # Safety window for delivery confirmation
                
    def dispatch_alert(self, alert_item, max_retries=3):
        name = alert_item["name"]
        ip = alert_item["ip"]
        status = alert_item["status"]
        phone = self.clean_phone_number(alert_item["phone"])

        if not phone:
            logger.error(f"Missing or corrupt phone data for {name}. Alert aborted.")
            return False

        msg = f"*{status}*\n\nDevice: {name}\nIP: {ip}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        logger.log(f"Opening chat payload viewport for {name} ({phone})...")

        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    logger.warn(f"🔄 Retrying transmission to {name} (Attempt {attempt}/{max_retries})...")
                
                self._attempt_delivery(phone, msg)
                logger.success(f"Alert successfully pushed to {phone} on attempt {attempt}")
                return True 
                
            except Exception as e:
                logger.error(f"Attempt {attempt} failed for {name}: {e}")
                if attempt == max_retries:
                    logger.error(f"❌ Final Delivery Defeat for {name} after {max_retries} cycles.")
                else:
                    time.sleep(5)
                    
        return False

    def close(self):
        try:
            self.driver.quit()
            logger.success("Chrome session killed safely.")
        except Exception:
            pass