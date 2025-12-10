"""Script to initialize the database with alembic migrations"""

import asyncio
import sys
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings
from src.database.base import Base

def init_db_with_alembic():
    """Initialize database using alembic migrations"""
    # Create alembic config
    alembic_cfg = Config("alembic.ini")

    # Set the database URL from settings
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

    # Generate the initial migration
    command.revision(alembic_cfg, autogenerate=True, message="Initial migration")

    # Run the migration to create tables
    command.upgrade(alembic_cfg, "head")

    print("Database initialized with alembic migrations successfully!")

if __name__ == "__main__":
    init_db_with_alembic()