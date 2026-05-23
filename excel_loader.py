import os
import pandas as pd
from config import EXCEL_FILE
from logger import logger

_last_mtime = 0
_cached_devices = []

def load_devices_if_changed():
    """
    Tracks modifications to your spreadsheet data safely.
    """
    global _last_mtime, _cached_devices
    config_changed = False
    
    try:
        if os.path.exists(EXCEL_FILE):
            current_mtime = os.path.getmtime(EXCEL_FILE)
            if current_mtime != _last_mtime:
                df = pd.read_excel(
                    EXCEL_FILE, 
                    dtype={"Contact Number": str, "IP Address": str, "Device Type": str}
                )
                
                # Replace float-converted fields or null instances up-front
                df = df.fillna("")
                
                _cached_devices = df.to_dict("records")
                _last_mtime = current_mtime
                config_changed = True
                logger.info("Excel configurations reloaded.")
                
    except Exception as e:
        logger.warn(f"Error reading excel file (might be locked/open): {e}")
        
    return _cached_devices, config_changed