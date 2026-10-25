import sys
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase

# Asegurar import de config tanto ejecutando desde Backend/ como desde raíz
try:
    from config import conf
except ModuleNotFoundError:
    from Backend.config import conf

# Motor asíncrono de SQLAlchemy
engine = create_async_engine(
    conf.async_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base declarativa para todos los modelos
class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Generador de dependencias para FastAPI que proporciona una sesión asíncrona de base de datos.
    Maneja el commit o rollback automático.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

