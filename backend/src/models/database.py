from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager


# Database connection setup
def get_database_engine(database_url: str):
    """Create a database engine with the given URL"""
    return create_engine(database_url, echo=False)


def get_async_database_engine(database_url: str):
    """Create an async database engine with the given URL"""
    return create_async_engine(database_url, echo=False)


# Create async session maker
async def get_async_session(database_url: str):
    """Create an async session for database operations"""
    engine = get_async_database_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session


# Base class for database models
Base = declarative_base()


# Dependency for getting database session in FastAPI
async def get_db_session():
    """Dependency to get database session"""
    from src.config.settings import settings
    async_session = await get_async_session(settings.neon_database_url)
    async with async_session() as session:
        yield session