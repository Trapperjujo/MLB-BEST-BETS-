import sys
import os
from loguru import logger

# Ensure the logs directory exists
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOG_FILE = os.path.join(LOGS_DIR, "terminal_2026.log")

# Configure Loguru
# 1. Console Output (Rich formatting)
# 2. File Output (Rotating, for historical troubleshooting)
logger.remove() # Remove default handler
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:7}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level="INFO")
logger.add(LOG_FILE, rotation="10 MB", retention="10 days", compression="zip", level="DEBUG")

def get_logger(name: str):
    return logger.bind(name=name)

# Global institutional logger
terminal_logger = get_logger("MLB-TERMINAL")
