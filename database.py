from typing import AsyncGenerator

from dotenv import load_dotenv
import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

load_dotenv()

DB_URL = os.environ["DB_URL"]
DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"

db_engine = create_async_engine(
    DB_URL,
    echo=DEBUG,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = async_sessionmaker(
    bind=db_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise