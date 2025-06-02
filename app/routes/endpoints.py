from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Target
from app.monitor import monitor_all_targets

router = APIRouter(prefix="/api", tags=["Targets"])

@router.get("/targets")
async def get_targets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Target))
    return result.scalars().all()

@router.post("/targets")
async def add_target(name: str, url: str, retry_count: int = 3, cooldown: int = 10, db: AsyncSession = Depends(get_db)):
    target = Target(name=name, url=url, retry_count=retry_count, cooldown=cooldown)
    db.add(target)
    await db.commit()
    await db.refresh(target)
    await monitor_all_targets()
    return target

@router.delete("/targets/{target_id}")
async def delete_target(target_id: int, db: AsyncSession = Depends(get_db)):
    target = await db.get(Target, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    await db.delete(target)
    await db.commit()
    return {"msg": "Target deleted"}
