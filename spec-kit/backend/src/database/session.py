from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config.settings import settings

# Create the database engine with environment-specific settings
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,  # Number of connections to maintain in the pool
    max_overflow=settings.db_max_overflow,  # Additional connections beyond pool_size
    pool_pre_ping=settings.db_pool_pre_ping,  # Verify connections before using them
    pool_recycle=settings.db_pool_recycle,  # Recycle connections after specified seconds
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency function that provides a database session for FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()