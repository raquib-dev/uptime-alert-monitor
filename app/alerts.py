 
import os
import aiohttp
from app.logger import logger

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_alert(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram alert skipped. Token or Chat ID missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    logger.info("Telegram alert sent.")
                else:
                    logger.error(f"Failed to send Telegram alert: {resp.status}")
        except Exception as e:
            logger.error(f"Telegram exception: {e}")
