from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config.settings import settings
from .base import Base

def init_database():
    """
    Initialize the database by creating all tables.
    This should be called when starting the application.
    """
    engine = create_engine(settings.database_url)

    # Create all tables defined in the models
    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully.")

if __name__ == "__main__":
    init_database()