import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

# Construct the MySQL async URL
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session maker
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Declarative base
Base = declarative_base()

# Dependency for getting DB session in routes
async def get_db():
    async with SessionLocal() as session:
        yield session
