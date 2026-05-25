# app_server.py

import threading
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# Core file structural imports 
from excel_loader import load_devices_if_changed
from network_utils import ping, check_sip_ports
from config import MAIN_PBX_IP, CHECK_INTERVAL_SECONDS

# Import the clean visual layout string cleanly split from our framework code
# Choice 1: For the Minimalist Cards Theme
from dashboard_minimal_cards import DASHBOARD_TEMPLATE

# Choice 2: For the Cyber-Hacker Matrix HUD
# from dashboard_hacker_hud import DASHBOARD_TEMPLATE

# Choice 3: For the Asymmetric Tactical Command Layout
# from dashboard_tactical_command import DASHBOARD_TEMPLATE

# Choice 4: For the Integrated Terminal Grid HUD
# from dashboard_terminal_hud import DASHBOARD_TEMPLATE

# Choice 5: For the Global SOC Threat Wall Theme
# from dashboard_soc_threat_wall import DASHBOARD_TEMPLATE

app = FastAPI(title="Infrastructure Fleet Operations Center")

# Global variables to pass state between engine background thread loops and web API
ui_device_cache = []
system_stats = {
    "total": 0, 
    "online": 0, 
    "offline": 0,
    "sip_failures": 0,
    "voip_count": 0,
    "camera_count": 0,
    "last_scan_epoch": 0,
    "scan_duration_ms": 0,
    "loop_cycle_count": 0
}

whatsapp_queue_stats = {
    "pending_count": 0,
    "sent_count": 0,
    "last_dispatched_to": "WAIT_IDLE",
    "last_msg_snippet": "System Initialized Safely // Scanning Subnets"
}

# Track previously alerted failures to prevent duplicate "sent_count" increments
already_alerted_nodes = set()

def background_monitoring_thread():
    """Runs inside background workspace safely isolated from the FastAPI server execution loop."""
    global ui_device_cache, system_stats, whatsapp_queue_stats, already_alerted_nodes
    cycle_counter = 0
    
    while True:
        try:
            cycle_counter += 1
            start_time = time.time()
            
            # Read from Excel data using modification rules tracking layer
            devices, _ = load_devices_if_changed()
            if not devices:
                time.sleep(5)
                continue
                
            temp_results = []
            online_count = 0
            sip_failures_count = 0
            voip_count = 0
            camera_count = 0
            current_failures_needing_alert = []
            current_failed_ips = set()
            
            for d in devices:
                ip = str(d.get("IP Address", "")).strip()
                name = d.get("Device Name", "Unknown Node")
                dtype = str(d.get("Device Type", "CAMERA")).upper()
                phone = d.get("Contact Number", "")
                
                if not ip or ip == "nan":
                    continue
                    
                if dtype == "VOIP":
                    voip_count += 1
                else:
                    camera_count += 1
                    
                # Evaluate ICMP State
                is_online = ping(ip)
                status_text = "ONLINE" if is_online else "OFFLINE"
                
                # Evaluate Secondary Application Layer Port SIP Protocol if Node is VoIP
                if is_online and dtype == "VOIP" and ip != MAIN_PBX_IP:
                    if not check_sip_ports(ip):
                        is_online = False
                        sip_failures_count += 1
                        status_text = "SIP REGISTRATION FAILED"
                        
                if is_online:
                    online_count += 1
                else:
                    current_failures_needing_alert.append((name, phone, status_text, ip))
                    current_failed_ips.add(ip)
                    
                temp_results.append({
                    "name": name,
                    "ip": ip,
                    "type": dtype,
                    "phone": phone,
                    "online": is_online,
                    "status": status_text
                })
                
            # Clean up old tracking flags for nodes that have recovered
            already_alerted_nodes = already_alerted_nodes.intersection(current_failed_ips)

            # Process Alert Triage Queue Metrics without infinite spamming
            if current_failures_needing_alert:
                whatsapp_queue_stats["pending_count"] = len(current_failures_needing_alert)
                
                # Target the first active threat in the array for layout presentation
                target_name, target_phone, target_reason, target_ip = current_failures_needing_alert[0]
                whatsapp_queue_stats["last_dispatched_to"] = f"{target_name} ({target_phone if target_phone else 'No Phone'})"
                whatsapp_queue_stats["last_msg_snippet"] = f"CRITICAL ALERT: [{target_name}] status is {target_reason}."
                
                # Only increment metrics counter if this is a newly discovered drop
                if target_ip not in already_alerted_nodes:
                    whatsapp_queue_stats["sent_count"] += 1
                    already_alerted_nodes.add(target_ip)
            else:
                whatsapp_queue_stats["pending_count"] = 0
                whatsapp_queue_stats["last_msg_snippet"] = "System operating within normal parameters. No anomalies flagged."

            duration_ms = int((time.time() - start_time) * 1000)
            
            # Commit calculations safely to global system memory
            ui_device_cache = temp_results
            system_stats = {
                "total": len(temp_results),
                "online": online_count,
                "offline": len(temp_results) - online_count,
                "sip_failures": sip_failures_count,
                "voip_count": voip_count,
                "camera_count": camera_count,
                "last_scan_epoch": int(time.time()),
                "scan_duration_ms": duration_ms,
                "loop_cycle_count": cycle_counter
            }
            
        except Exception as e:
            print(f"Engine Daemon Thread Exception Encountered: {e}")
            
        time.sleep(CHECK_INTERVAL_SECONDS)

# Launch background multi-threaded monitoring pipeline loop automatically during server startup
@app.on_event("startup")
def start_monitor_backend():
    t = threading.Thread(target=background_monitoring_thread, daemon=True)
    t.start()

@app.get("/api/data")
def get_live_telemetry():
    """Asynchronous secure endpoint exposing global memory metrics variables directly to frontend JS layout."""
    return {
        "stats": system_stats, 
        "devices": ui_device_cache,
        "whatsapp": whatsapp_queue_stats,
        "config": {
            "main_pbx_ip": MAIN_PBX_IP,
            "check_interval": CHECK_INTERVAL_SECONDS
        }
    }

@app.get("/", response_class=HTMLResponse)
def render_dashboard_frontend():
    """Serves the decoupled dashboard UI code string variables directly from code-split layout modules."""
    return DASHBOARD_TEMPLATE

if __name__ == "__main__":
    uvicorn.run("app_server:app", host="0.0.0.0", port=8000, reload=True)