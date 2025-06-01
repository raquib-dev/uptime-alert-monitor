 
import asyncio
from app.monitor import monitor_all_targets
from app.logger import logger

async def start_scheduler():
    async def loop():
        while True:
            try:
                await monitor_all_targets()
                await asyncio.sleep(60)  # every 60 seconds
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(10)
    
    asyncio.create_task(loop())
