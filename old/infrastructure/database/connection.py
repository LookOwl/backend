from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import sessionmaker
from old.infrastructure.config.config import settings

# Establecemos conexión con la base de datos
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,            
    echo=settings.debug,
)

async_session_factory  = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,         
    autoflush=False,              
    autocommit=False,
)