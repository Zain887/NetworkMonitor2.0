import os

# Project Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE_DIR, "whatsapp_selenium_profile")

# Files
EXCEL_FILE = "cameras.xlsx"

# Monitoring Metrics
CHECK_INTERVAL_SECONDS = 30
MAX_THREADS = 25
FAILURE_THRESHOLD = 2  # 2 failed scans = ALERT TRIGGER

# IP Routing Hardware Target Core
MAIN_PBX_IP = "192.168.3.2"

# SIP Signaling
SIP_PORTS = [5060, 5927]
SIP_TIMEOUT = 2