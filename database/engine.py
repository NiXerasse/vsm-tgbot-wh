from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config.env import db_url
from database.models import Base

engine = create_async_engine(db_url, echo=False)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
