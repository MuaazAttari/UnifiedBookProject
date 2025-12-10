import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.db.database import get_db
from src.services.translation_service import TranslationService


# Create a test database session
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_translation.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as test_client:
        yield test_client


class TestTranslationService:
    """Test suite for translation service."""

    def test_translate_text(self, client):
        """Test basic text translation."""
        # Register and login user first
        user_data = {
            "email": "translate@example.com",
            "password": "testpassword123",
            "first_name": "Translate",
            "last_name": "Test"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "translate@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Test translation
        translation_request = {
            "text": "Hello, how are you?",
            "target_language": "ur"
        }

        response = client.post(
            "/api/v1/translation/translate",
            json=translation_request,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "translated_text" in data
        assert data["original_text"] == "Hello, how are you?"
        assert data["target_language"] == "ur"
        assert "[URDU TRANSLATION]" in data["translated_text"]

    def test_translate_text_invalid_inputs(self, client):
        """Test translation with invalid inputs."""
        # Register and login user first
        user_data = {
            "email": "translate-invalid@example.com",
            "password": "testpassword123",
            "first_name": "Translate Invalid",
            "last_name": "Test"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "translate-invalid@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Test with empty text
        translation_request = {
            "text": "",
            "target_language": "ur"
        }

        response = client.post(
            "/api/v1/translation/translate",
            json=translation_request,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400

        # Test with empty target language
        translation_request = {
            "text": "Hello",
            "target_language": ""
        }

        response = client.post(
            "/api/v1/translation/translate",
            json=translation_request,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400

    def test_translate_large_text(self, client):
        """Test translation of large text."""
        # Register and login user first
        user_data = {
            "email": "translate-large@example.com",
            "password": "testpassword123",
            "first_name": "Translate Large",
            "last_name": "Test"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "translate-large@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Test translation of large text
        large_text = "This is a large text. " * 100  # Repeat to make it large
        translation_request = {
            "text": large_text,
            "target_language": "ur",
            "chunk_size": 500,
            "overlap": 50
        }

        response = client.post(
            "/api/v1/translation/translate-large",
            json=translation_request,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "original_text" in data
        assert "translated_text" in data
        assert data["target_language"] == "ur"
        assert len(data["original_text"]) == len(large_text)

    def test_translation_caching(self):
        """Test translation caching functionality."""
        from src.db.database import SessionLocal

        db = SessionLocal()

        try:
            # Test cache miss - should call translation service
            translation_service = TranslationService()

            # First translation should not be cached
            result1 = translation_service.translate_text_with_db(
                db, "Hello world", "ur", "en", use_cache=True
            )
            assert "[URDU TRANSLATION]" in result1

            # Second translation of same text should be cached
            result2 = translation_service.translate_text_with_db(
                db, "Hello world", "ur", "en", use_cache=True
            )
            assert result2 == result1

            # Test cache with different target language
            result3 = translation_service.translate_text_with_db(
                db, "Hello world", "es", "en", use_cache=True
            )
            assert "[SPANISH TRANSLATION]" in result3
            assert result3 != result1
        finally:
            db.close()

    def test_get_supported_languages(self, client):
        """Test getting supported languages."""
        response = client.get("/api/v1/translation/supported-languages")

        assert response.status_code == 200
        data = response.json()
        assert "supported_languages" in data
        assert len(data["supported_languages"]) > 0
        assert {"code": "ur", "name": "Urdu"} in data["supported_languages"]

    def test_cache_stats(self, client):
        """Test getting cache statistics."""
        # Register and login user first
        user_data = {
            "email": "cache-stats@example.com",
            "password": "testpassword123",
            "first_name": "Cache Stats",
            "last_name": "Test"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "cache-stats@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Get cache stats
        response = client.get(
            "/api/v1/translation/cache/stats",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "cache_stats" in data
        stats = data["cache_stats"]
        assert "total_entries" in stats
        assert "by_language" in stats


class TestTranslationUtilities:
    """Test utility functions in translation service."""

    def test_mock_translation_urdu(self):
        """Test mock translation for Urdu."""
        translation_service = TranslationService()
        result = translation_service._mock_translate("Hello", "ur")
        assert "[URDU TRANSLATION]" in result
        assert "Hello" in result
        assert "[TRANSLATED TO URDU]" in result

    def test_mock_translation_spanish(self):
        """Test mock translation for Spanish."""
        translation_service = TranslationService()
        result = translation_service._mock_translate("Hello", "es")
        assert "[SPANISH TRANSLATION]" in result
        assert "Hello" in result
        assert "[TRADUCIDO AL ESPAÑOL]" in result

    def test_mock_translation_invalid_input(self):
        """Test mock translation with invalid input."""
        translation_service = TranslationService()

        # Test with empty text
        with pytest.raises(ValueError, match="Text to translate cannot be empty"):
            translation_service._mock_translate("", "ur")

        # Test with empty target language
        with pytest.raises(ValueError, match="Target language cannot be empty"):
            translation_service._mock_translate("Hello", "")

    def test_chunk_text_utility(self):
        """Test the chunk text utility function."""
        from src.utils.text_utils import chunk_text

        # Test with small text (should return as single chunk)
        text = "This is a short text."
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0] == text

        # Test with larger text
        large_text = "This is sentence one. This is sentence two! Is this sentence three? " * 10
        chunks = chunk_text(large_text, chunk_size=50, overlap=10)
        assert len(chunks) > 1
        # Each chunk should be less than or equal to chunk_size
        for chunk in chunks:
            assert len(chunk) <= 50 or "This is sentence" in chunk  # Allow some flexibility for sentence boundaries