
from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TypeDecorator, JSON

from app.core.config import settings

class Base(DeclarativeBase):
    pass

class VectorType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def __init__(self, dim: int = 384, **kwargs):
        super().__init__(**kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from pgvector.sqlalchemy import Vector
                return dialect.type_descriptor(Vector(self.dim))
            except ImportError:
                return dialect.type_descriptor(JSON())
        return dialect.type_descriptor(JSON())

class LazyEngineProxy:
    def __init__(self):
        self._engine: AsyncEngine | None = None

    def get_engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                future=True,
                pool_pre_ping=True,
            )
        return self._engine

    async def dispose(self):
        if self._engine is not None:
            await self._engine.dispose()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.get_engine(), name)

class LazySessionMakerProxy:
    def __init__(self, engine_proxy: LazyEngineProxy):
        self._engine_proxy = engine_proxy
        self._maker: Any = None

    def get_maker(self):
        if self._maker is None:
            self._maker = async_sessionmaker(
                bind=self._engine_proxy.get_engine(),
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
        return self._maker

    def __call__(self, *args, **kwargs):
        return self.get_maker()(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.get_maker(), name)

engine = LazyEngineProxy()
AsyncSessionLocal = LazySessionMakerProxy(engine)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
