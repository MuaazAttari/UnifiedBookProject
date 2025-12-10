import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.database.session import Base
from src.config.settings import settings


# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create the database tables
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def db():
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()

    # Bind the session to the connection
    db_session = TestingSessionLocal(bind=connection)

    yield db_session

    # Rollback the transaction after the test
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client