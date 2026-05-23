import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

from config import MAX_THREADS, FAILURE_THRESHOLD, CHECK_INTERVAL_SECONDS
from excel_loader import load_devices_if_changed
from logger import logger
from network_utils import ping, check_sip_ports
from whatsapp import WhatsAppSender

# Global alert pipe
alert_queue = queue.Queue()

def check_device(device):
    """
    Executes isolated check steps across a single device record map context.
    """
    try:
        # Enforce exact string parsing to match your single file logic
        ip = str(device.get("IP Address", "")).strip()
        name = device.get("Device Name", "Unknown Device")
        phone = device.get("Contact Number", "")
        dtype = str(device.get("Device Type", "CAMERA")).strip().upper()
        
        if not ip or pd.isna(device.get("IP Address")) or ip == "nan":
            return None
        
        # 1. Check physical hardware connectivity via Ping
        is_online = ping(ip)
        status_flag = "ONLINE" if is_online else "OFFLINE"
        
        # 2. Match exact hardcoded IP string to bypass the GrandStream Exchange server
        if is_online and dtype == "VOIP" and ip != "192.168.3.2":
            sip_working = check_sip_ports(ip, ports=[5060, 5927], timeout=2)
            if not sip_working:
                is_online = False
                status_flag = "SIP REGISTRATION FAILED"
                
        return {
            "name": name, 
            "ip": ip, 
            "phone": phone, 
            "type": dtype, 
            "online": is_online, 
            "status_flag": status_flag
        }
    except Exception as e:
        logger.error(f"Worker processing error: {e}")
        return None


def main():
    device_state = {}
    failure_count = {}
    
    # Instantiate the communication interface
    whatsapp_engine = WhatsAppSender()
    logger.alert("Monitoring loop fully engaged...")

    try:
        while True:
            try:
                devices, updated = load_devices_if_changed()
                if not devices:
                    time.sleep(5)
                    continue

                if updated:
                    active_ips = {str(d.get("IP Address", "")).strip() for d in devices if pd.notna(d.get("IP Address"))}
                    orphaned_ips = set(device_state.keys()) - active_ips
                    for old_ip in orphaned_ips:
                        logger.warn(f"Purging dropped device {old_ip} from memory.")
                        device_state.pop(old_ip, None)
                        failure_count.pop(old_ip, None)

                results = []
                with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                    futures = [executor.submit(check_device, d) for d in devices]
                    for f in as_completed(futures):
                        res = f.result()
                        if res:
                            results.append(res)

                # ===== PROCESS DIAGNOSTIC RESULTS =====
                for r in results:
                    ip = r["ip"]
                    name = r["name"]
                    phone = r["phone"]
                    online = r["online"]
                    status_flag = r["status_flag"]

                    # --- INITIALIZATION LOGIC ---
                    if ip not in device_state:
                        device_state[ip] = online
                        
                        if not online:
                            failure_count[ip] = FAILURE_THRESHOLD
                            logger.alert(f"INIT {name} ({ip}) is ALREADY {status_flag} at startup! Queueing alert...")
                            
                            if status_flag == "SIP REGISTRATION FAILED":
                                startup_msg = "STARTUP ALERT: SIP REGISTRATION FAILED\n\nExtension Registration is Frozen"
                            elif ip == "192.168.3.2":
                                startup_msg = "STARTUP CRITICAL ALERT\n\nGrandStream UCM6108 is Hang Need to be Restart Device"
                            else:
                                startup_msg = "STARTUP ALERT: OFFLINE\n\nDevice is Unresponsive"
                                
                            alert_queue.put({"name": name, "ip": ip, "status": startup_msg, "phone": phone})
                        else:
                            failure_count[ip] = 0
                            logger.success(f"INIT {name} ({ip}) → ONLINE")
                        continue

                    # --- NORMAL RUNNING LOGIC ---
                    if online:
                        if not device_state[ip]:
                            logger.success(f"RECOVERED: {name} (Queueing Alert)")
                            alert_queue.put({"name": name, "ip": ip, "status": "RECOVERED ALERT", "phone": phone})
                        device_state[ip] = True
                        failure_count[ip] = 0
                    else:
                        failure_count[ip] += 1
                        logger.warn(f"FAIL {name} ({failure_count[ip]}/{FAILURE_THRESHOLD}) - Reason: {status_flag}")

                        if failure_count[ip] == FAILURE_THRESHOLD and device_state[ip]:
                            device_state[ip] = False
                            
                            # Extension Interception Core Rules Override
                            if ip.startswith("192.168.3.") and ip != "192.168.3.2":
                                logger.log(f"🔍 Extension down ({name}). Checking GrandStream Main Server status...")
                                main_server_online = ping("192.168.3.2")
                                
                                if not main_server_online:
                                    logger.alert("CRITICAL: GrandStream Main Server is completely unreachable! Overriding with Server Hang alert.")
                                    alert_queue.put({
                                        "name": "GrandStream UCM6108",
                                        "ip": "192.168.3.2",
                                        "status": "CRITICAL ALERT\n\nGrandStram UCM6108 is Hang Need to be Restart Device",
                                        "phone": phone
                                    })
                                    continue
                            
                            if status_flag == "SIP REGISTRATION FAILED":
                                final_msg = "SIP REGISTRATION FAILED ALERT\n\nExtension Registration Dropped or Frozen"
                            elif ip == "192.168.3.2":
                                final_msg = "CRITICAL ALERT\n\nGrandStram UCM6108 is Hang Need to be Restart Device"
                            else:
                                final_msg = "OFFLINE ALERT\n\nDevice is Unresponsive"

                            logger.alert(f"Queueing notification text for {name}")
                            alert_queue.put({"name": name, "ip": ip, "status": final_msg, "phone": phone})

                # ===== CONSUME QUEUED ALERTS SEQUENTIALLY =====
                if not alert_queue.empty():
                    logger.log(f"📦 Processing {alert_queue.qsize()} pending notification(s)...")
                    while not alert_queue.empty():
                        item = alert_queue.get()
                        whatsapp_engine.dispatch_alert(item)
                        alert_queue.task_done()

            except Exception as loop_err:
                logger.error(f"CRITICAL failure inside loop execution context: {loop_err}")

            time.sleep(CHECK_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        logger.warn("Manual shutdown signal caught. Cleaning resources...")
    finally:
        whatsapp_engine.close()

if __name__ == "__main__":
    main()