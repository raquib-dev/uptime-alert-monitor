import logging
from pathlib import Path
import sys

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create log file handler (UTF-8 supports emojis)
file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

# Create safe console handler (no emojis)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger = logging.getLogger("uptime-monitor")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
