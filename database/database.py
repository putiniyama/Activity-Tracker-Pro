from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from config.config import settings
from .models import Base

# Создаем асинхронный движок
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Получение сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 