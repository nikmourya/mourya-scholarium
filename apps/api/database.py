"""
Mourya Scholarium — Database Connection & Session Management
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import settings

# SQLite doesn't support pool_size / max_overflow
engine_kwargs = {"echo": settings.app_debug}
if not settings.use_sqlite:
    engine_kwargs.update({"pool_size": 20, "max_overflow": 10})

engine = create_async_engine(settings.database_url, **engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables — use Alembic in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
