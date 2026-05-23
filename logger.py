import os
import time
import logging

# Ensure a dedicated logs folder exists inside your directory
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "monitor.log")

# Configure the built-in logging system for file output
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class ConsoleLogger:
    @staticmethod
    def _write(prefix: str, msg: str, level: str = "info"):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        full_msg = f"{prefix} {msg}"
        
        # 1. Print directly to your command prompt terminal screen
        print(full_msg)
        
        # 2. Silently mirror the text clean into the logs/monitor.log file
        if level == "error" or level == "critical":
            logging.error(msg)
        elif level == "warning":
            logging.warning(msg)
        else:
            logging.info(msg)

    def info(self, msg: str):
        self._write("ℹ️", msg, "info")

    def success(self, msg: str):
        self._write("✅", msg, "info")

    def warn(self, msg: str):
        self._write("⚠️", msg, "warning")

    def error(self, msg: str):
        self._write("❌", msg, "error")

    def alert(self, msg: str):
        self._write("🚨", msg, "warning")

    def log(self, msg: str):
        # General layout messages without icons
        print(msg)
        logging.info(msg)

# Global Instance
logger = ConsoleLogger()