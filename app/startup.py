import asyncio
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models import User
from sqlalchemy.future import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_default_admin():
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        existing = result.scalar()
        if not existing:
            admin = User(
                username="admin",
                hashed_password=pwd_context.hash("@dm!n123"),
                is_admin=True
            )
            session.add(admin)
            await session.commit()
