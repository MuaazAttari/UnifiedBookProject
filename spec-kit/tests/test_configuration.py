import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from src.db.database import Base
from src.models.configuration import Configuration
from src.services.configuration_service import ConfigurationService


# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a clean database for testing."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_configuration(db):
    """Test creating a configuration."""
    config = ConfigurationService.create_configuration(
        db=db,
        constitution_path="./.specify/memory/constitution.md",
        history_path="history/prompts/",
        spec_folder=".",
        docs_folder="../my-website/docs/",
        assets_folder="../my-website/static/",
        root_folder="../"
    )

    assert config.config_id is not None
    assert config.constitution_path == "./.specify/memory/constitution.md"
    assert config.history_path == "history/prompts/"
    assert config.spec_folder == "."
    assert config.docs_folder == "../my-website/docs/"
    assert config.assets_folder == "../my-website/static/"
    assert config.root_folder == "../"


def test_get_configuration(db):
    """Test retrieving a configuration by ID."""
    # Create a configuration first
    created_config = ConfigurationService.create_configuration(
        db=db,
        constitution_path="./.specify/memory/constitution.md",
        history_path="history/prompts/",
        spec_folder=".",
        docs_folder="../my-website/docs/",
        assets_folder="../my-website/static/",
        root_folder="../"
    )

    # Retrieve it by ID
    retrieved_config = ConfigurationService.get_configuration(
        db, created_config.config_id
    )

    assert retrieved_config is not None
    assert retrieved_config.config_id == created_config.config_id
    assert retrieved_config.constitution_path == "./.specify/memory/constitution.md"


def test_get_configuration_by_path(db):
    """Test retrieving a configuration by docs folder path."""
    docs_folder = "../my-website/docs/"

    # Create a configuration
    created_config = ConfigurationService.create_configuration(
        db=db,
        constitution_path="./.specify/memory/constitution.md",
        history_path="history/prompts/",
        spec_folder=".",
        docs_folder=docs_folder,
        assets_folder="../my-website/static/",
        root_folder="../"
    )

    # Retrieve it by path
    retrieved_config = ConfigurationService.get_configuration_by_path(
        db, docs_folder
    )

    assert retrieved_config is not None
    assert retrieved_config.config_id == created_config.config_id
    assert retrieved_config.docs_folder == docs_folder


def test_update_configuration(db):
    """Test updating an existing configuration."""
    # Create a configuration
    original_config = ConfigurationService.create_configuration(
        db=db,
        constitution_path="./.specify/memory/constitution.md",
        history_path="history/prompts/",
        spec_folder=".",
        docs_folder="../my-website/docs/",
        assets_folder="../my-website/static/",
        root_folder="../"
    )

    # Update it
    updated_config = ConfigurationService.update_configuration(
        db=db,
        config_id=original_config.config_id,
        constitution_path="./new/constitution.md",
        history_path="new/history/prompts/"
    )

    assert updated_config is not None
    assert updated_config.config_id == original_config.config_id
    assert updated_config.constitution_path == "./new/constitution.md"
    assert updated_config.history_path == "new/history/prompts/"


def test_delete_configuration(db):
    """Test deleting a configuration."""
    # Create a configuration
    config = ConfigurationService.create_configuration(
        db=db,
        constitution_path="./.specify/memory/constitution.md",
        history_path="history/prompts/",
        spec_folder=".",
        docs_folder="../my-website/docs/",
        assets_folder="../my-website/static/",
        root_folder="../"
    )

    # Verify it exists
    retrieved_config = ConfigurationService.get_configuration(
        db, config.config_id
    )
    assert retrieved_config is not None

    # Delete it
    deleted = ConfigurationService.delete_configuration(
        db, config.config_id
    )
    assert deleted is True

    # Verify it's gone
    retrieved_config = ConfigurationService.get_configuration(
        db, config.config_id
    )
    assert retrieved_config is None


def test_path_validation():
    """Test path validation functionality."""
    from src.utils.path_validator import validate_path_exists, validate_paths_structure

    # Test with a path that doesn't exist
    result = validate_path_exists("/non/existent/path")
    assert result is False

    # Test with the current directory which should exist
    result = validate_path_exists(".")
    assert result is True

    # Test multiple paths
    paths = {
        "current_dir": ".",
        "parent_dir": "..",
        "nonexistent": "/non/existent/path"
    }
    results = validate_paths_structure(paths)

    assert results["current_dir"] is True
    assert results["parent_dir"] is True
    assert results["nonexistent"] is False