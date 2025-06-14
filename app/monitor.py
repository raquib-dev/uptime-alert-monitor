import aiohttp
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.models import Target, PingHistory
from app.database import SessionLocal
from app.alerts import send_telegram_alert
from app.logger import logger

async def ping_target(session: aiohttp.ClientSession, target: Target) -> tuple:
    try:
        start = datetime.now()
        async with session.get(target.url, timeout=10) as response:
            end = datetime.now()
            response_time = (end - start).total_seconds()
            return True, response_time
    except Exception:
        return False, None

async def process_target(target: Target, session: aiohttp.ClientSession):
    async with SessionLocal() as db:
        success = False
        response_time = None

        for attempt in range(target.retry_count):
            success, response_time = await ping_target(session, target)
            if success:
                target.last_status = True
                target.last_response_time = response_time
                target.last_checked = datetime.now()
                db.add(target)
                await db.commit()

                logger.info(f"[✅ UP] {target.name} | {target.url} | {response_time:.2f}s")
                break

            await asyncio.sleep(target.cooldown)

        if not success:
            if target.last_status is not False:
                logger.warning(f"[❌ DOWN] {target.name} | {target.url}")
                await send_telegram_alert(f"🚨 Target DOWN: {target.name}\n{target.url}")

            target.last_status = False
            target.last_response_time = None
            target.last_checked = datetime.now()
            db.add(target)
            await db.commit()

        ping = PingHistory(
            target_id=target.id,
            status=success,
            response_time=response_time,
            checked_at=datetime.now()
        )
        db.add(ping)
        await db.commit()

async def monitor_all_targets():
    async with aiohttp.ClientSession() as session:
        result_targets = []

        # Create a temporary session to fetch targets first
        async with SessionLocal() as db:
            result = await db.execute(select(Target))
            result_targets = result.scalars().all()

        # Now process each target using a NEW DB session per task
        await asyncio.gather(*[
            process_target(target, session) for target in result_targets
        ])