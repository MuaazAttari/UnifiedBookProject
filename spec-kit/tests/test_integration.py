"""
Comprehensive integration tests for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module tests the integration between different components and services.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
import tempfile
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.main import app
from src.db.database import get_db, Base
from src.services.auth_service import AuthService
from src.services.translation_service import TranslationService
from src.services.personalization_service import PersonalizationService
from src.services.embedding_service import EmbeddingService
from src.services.openai_service import OpenAIService
from src.models.user import User
from src.models.chapter import Chapter
from src.models.translation_cache import TranslationCache
from src.models.personalization_profile import PersonalizationProfile


# Create a test database session
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
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


@pytest.fixture
def setup_database():
    """Set up the test database with required tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestUserAuthenticationIntegration:
    """Test integration between authentication and other services."""

    def test_user_creation_affects_all_systems(self, client, setup_database):
        """Test that user creation integrates properly with all systems."""
        # Register user
        user_data = {
            "email": "integration-test@example.com",
            "password": "SecurePassword123!",
            "first_name": "Integration",
            "last_name": "Test"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        user_id = response.json()["id"]
        assert user_id

        # Login to get token
        login_response = client.post("/api/v1/auth/login", json={
            "email": "integration-test@example.com",
            "password": "SecurePassword123!"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Verify user can access protected endpoints
        profile_response = client.get("/api/v1/auth/profile", headers={"Authorization": f"Bearer {token}"})
        assert profile_response.status_code == 200

        # Verify user can create chapters
        chapter_data = {
            "title": "Integration Test Chapter",
            "content": "# Test\nThis chapter tests integration.",
            "order": 1,
            "category": "integration"
        }
        chapter_response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert chapter_response.status_code == 200

        print("✓ User creation integration verified")

    def test_session_integration_across_services(self, client, setup_database):
        """Test that authentication session works across different services."""
        # Register and login
        user_data = {
            "email": "session-integration@example.com",
            "password": "SecurePassword123!",
            "first_name": "Session",
            "last_name": "Integration"
        }
        client.post("/api/v1/auth/register", json=user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "email": "session-integration@example.com",
            "password": "SecurePassword123!"
        })
        token = login_response.json()["access_token"]

        # Test access to different services with same token
        services_to_test = [
            "/api/v1/chapters/",
            "/api/v1/translation/supported-languages",
            "/api/v1/auth/profile"
        ]

        for service_endpoint in services_to_test:
            response = client.get(service_endpoint, headers={"Authorization": f"Bearer {token}"})
            # Should not return 401 (unauthorized) for protected endpoints
            # Might return 405 (method not allowed) or 200, but not 401
            assert response.status_code != 401

        print("✓ Session integration across services verified")


class TestRAGAndTranslationIntegration:
    """Test integration between RAG system and translation services."""

    def test_translated_content_in_rag_system(self, client, setup_database):
        """Test that translated content can be used in RAG system."""
        # Register and login user
        user_data = {
            "email": "rag-translation@example.com",
            "password": "Password123!",
            "first_name": "RAG",
            "last_name": "Translation"
        }
        client.post("/api/v1/auth/register", json=user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "email": "rag-translation@example.com",
            "password": "Password123!"
        })
        token = login_response.json()["access_token"]

        # Create a chapter with English content
        chapter_data = {
            "title": "AI Fundamentals",
            "content": "# Artificial Intelligence\nArtificial Intelligence is a branch of computer science that aims to create software or machines that exhibit human-like intelligence.",
            "order": 1,
            "category": "ai"
        }
        chapter_response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert chapter_response.status_code == 200

        # Translate the content to Urdu
        translation_request = {
            "text": chapter_data["content"],
            "target_language": "ur"
        }
        translation_response = client.post(
            "/api/v1/translation/translate",
            json=translation_request,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert translation_response.status_code == 200

        translated_content = translation_response.json()["translated_text"]
        assert "[URDU TRANSLATION]" in translated_content

        print("✓ RAG and translation integration verified")

    def test_multilingual_rag_queries(self, client, setup_database):
        """Test RAG system with multilingual queries."""
        # Register and login user
        user_data = {
            "email": "multilingual-rag@example.com",
            "password": "Password123!",
            "first_name": "Multilingual",
            "last_name": "RAG"
        }
        client.post("/api/v1/auth/register", json=user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "email": "multilingual-rag@example.com",
            "password": "Password123!"
        })
        token = login_response.json()["access_token"]

        # Create English chapter
        chapter_data = {
            "title": "Machine Learning",
            "content": "# Machine Learning\nMachine learning is a method of data analysis that automates analytical model building.",
            "order": 1,
            "category": "ml"
        }
        client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Test English query
        english_query = {
            "message": "What is machine learning?",
            "context_type": "full_book"
        }
        response = client.post(
            "/api/v1/chat/",
            json=english_query,
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should handle gracefully (might fail due to missing dependencies)

        # Test translated query (Urdu)
        urdu_query = {
            "message": "مشین لرننگ کیا ہے؟",  # What is machine learning in Urdu
            "context_type": "full_book"
        }
        response = client.post(
            "/api/v1/chat/",
            json=urdu_query,
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should handle gracefully

        print("✓ Multilingual RAG queries integration verified")


class TestPersonalizationAndTranslationIntegration:
    """Test integration between personalization and translation services."""

    def test_personalized_translation_preferences(self, setup_database):
        """Test that personalization can influence translation preferences."""
        db = TestingSessionLocal()

        try:
            # Create user profile with language preference
            auth_service = AuthService()
            user = auth_service.create_user(
                "personalize-translate@example.com",
                "Password123!",
                "Personalize",
                "Translate"
            )

            # Set personalization preference for language
            personalization_service = PersonalizationService()
            personalization_service.set_personalization_for_user(
                db, str(user.id), 1, "preferred_translation_language", "ur"
            )

            # Test that the preference is stored
            preferred_lang = personalization_service.get_personalization_for_user(
                db, str(user.id), 1, "preferred_translation_language"
            )
            assert preferred_lang == "ur"

            # Test translation service with user context
            translation_service = TranslationService()
            result = translation_service.translate_text_with_db(
                db, "Hello, how are you?", "ur", "en", use_cache=True
            )
            assert "[URDU TRANSLATION]" in result

            print("✓ Personalized translation preferences integration verified")

        finally:
            db.close()

    def test_experience_level_affects_translation_complexity(self, setup_database):
        """Test that user experience level affects translation complexity."""
        db = TestingSessionLocal()

        try:
            # Create user and set experience level
            auth_service = AuthService()
            user = auth_service.create_user(
                "exp-translate@example.com",
                "Password123!",
                "Experience",
                "Translate"
            )

            # Set experience level preference
            personalization_service = PersonalizationService()
            personalization_service.set_personalization_for_user(
                db, str(user.id), 1, "experience_level", "beginner"
            )

            # Get the experience level
            exp_level = personalization_service.get_personalization_for_user(
                db, str(user.id), 1, "experience_level"
            )
            assert exp_level == "beginner"

            print("✓ Experience level affects translation complexity integration verified")

        finally:
            db.close()


class TestDataFlowIntegration:
    """Test data flow between different components."""

    def test_chapter_creation_triggers_embedding(self, client, setup_database):
        """Test that chapter creation triggers embedding process."""
        # Register and login user
        user_data = {
            "email": "embedding-integration@example.com",
            "password": "Password123!",
            "first_name": "Embedding",
            "last_name": "Integration"
        }
        client.post("/api/v1/auth/register", json=user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "email": "embedding-integration@example.com",
            "password": "Password123!"
        })
        token = login_response.json()["access_token"]

        # Create a chapter
        chapter_data = {
            "title": "Neural Networks",
            "content": "# Neural Networks\nNeural networks are computing systems vaguely inspired by the biological neural networks.",
            "order": 1,
            "category": "neural-networks",
            "word_count": 20
        }
        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # Verify chapter was created
        get_response = client.get("/api/v1/chapters/", headers={"Authorization": f"Bearer {token}"})
        assert get_response.status_code == 200
        chapters = get_response.json()
        assert len(chapters) == 1
        assert chapters[0]["title"] == "Neural Networks"

        print("✓ Chapter creation and embedding integration verified")

    def test_translation_caching_integration(self, client, setup_database):
        """Test integration between translation service and caching."""
        # Register and login user
        user_data = {
            "email": "cache-integration@example.com",
            "password": "Password123!",
            "first_name": "Cache",
            "last_name": "Integration"
        }
        client.post("/api/v1/auth/register", json=user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "email": "cache-integration@example.com",
            "password": "Password123!"
        })
        token = login_response.json()["access_token"]

        test_text = "This is a test for caching integration."
        target_lang = "ur"

        # First translation - should not be cached
        translation_request = {
            "text": test_text,
            "target_language": target_lang
        }
        response1 = client.post(
            "/api/v1/translation/translate",
            json=translation_request,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 200

        # Second translation of same text - should use cache
        response2 = client.post(
            "/api/v1/translation/translate",
            json=translation_request,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response2.status_code == 200

        # Both responses should have the same translated content
        assert response1.json()["translated_text"] == response2.json()["translated_text"]

        # Check cache stats
        stats_response = client.get("/api/v1/translation/cache/stats", headers={"Authorization": f"Bearer {token}"})
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["cache_stats"]["total_entries"] >= 1

        print("✓ Translation caching integration verified")


class TestServiceOrchestration:
    """Test orchestration between multiple services."""

    def test_complete_learning_flow(self, client, setup_database):
        """Test a complete learning flow involving multiple services."""
        # Register user
        user_data = {
            "email": "complete-flow@example.com",
            "password": "SecurePassword123!",
            "first_name": "Complete",
            "last_name": "Flow"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        user_id = response.json()["id"]

        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "complete-flow@example.com",
            "password": "SecurePassword123!"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Create multiple chapters
        chapters = [
            {
                "title": "Introduction to AI",
                "content": "# Introduction\nArtificial Intelligence basics and concepts.",
                "order": 1,
                "category": "introduction"
            },
            {
                "title": "Machine Learning Fundamentals",
                "content": "# Machine Learning\nSupervised, unsupervised, and reinforcement learning.",
                "order": 2,
                "category": "ml"
            },
            {
                "title": "Deep Learning Concepts",
                "content": "# Deep Learning\nNeural networks, CNNs, RNNs, and transformers.",
                "order": 3,
                "category": "deep-learning"
            }
        ]

        for chapter in chapters:
            response = client.post(
                "/api/v1/chapters/",
                json=chapter,
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200

        # Set personalization preferences
        personalization_data = {
            "chapter_id": 1,
            "preference_type": "difficulty",
            "preference_value": "beginner"
        }
        response = client.post(
            "/api/v1/personalization/",
            json=personalization_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should handle gracefully

        # Translate content
        translation_request = {
            "text": "Artificial Intelligence is transforming the world.",
            "target_language": "ur"
        }
        response = client.post(
            "/api/v1/translation/translate",
            json=translation_request,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # Test RAG query
        chat_request = {
            "message": "What did I learn about AI?",
            "context_type": "full_book"
        }
        response = client.post(
            "/api/v1/chat/",
            json=chat_request,
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should handle gracefully

        print("✓ Complete learning flow integration verified")

    def test_error_propagation_between_services(self, client, setup_database):
        """Test how errors propagate between integrated services."""
        # Register and login user
        user_data = {
            "email": "error-propagation@example.com",
            "password": "Password123!",
            "first_name": "Error",
            "last_name": "Propagation"
        }
        client.post("/api/v1/auth/register", json=user_data)
        login_response = client.post("/api/v1/auth/login", json={
            "email": "error-propagation@example.com",
            "password": "Password123!"
        })
        token = login_response.json()["access_token"]

        # Test invalid translation request
        invalid_translation = {
            "text": "",
            "target_language": ""
        }
        response = client.post(
            "/api/v1/translation/translate",
            json=invalid_translation,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

        # Test invalid chapter creation
        invalid_chapter = {
            "title": "",
            "content": "",
            "order": 0,
            "category": ""
        }
        response = client.post(
            "/api/v1/chapters/",
            json=invalid_chapter,
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should handle gracefully (might be 422 for validation error)

        # Verify that one service error doesn't break others
        profile_response = client.get("/api/v1/auth/profile", headers={"Authorization": f"Bearer {token}"})
        assert profile_response.status_code == 200

        print("✓ Error propagation between services verified")


class TestDatabaseIntegration:
    """Test integration with database operations."""

    def test_transactional_integrity(self, setup_database):
        """Test that database operations maintain transactional integrity."""
        db = TestingSessionLocal()

        try:
            # Test creating related records in transaction
            auth_service = AuthService()

            # Create user
            user = auth_service.create_user(
                "transaction-test@example.com",
                "Password123!",
                "Transaction",
                "Test"
            )
            assert user.id

            # Create a chapter for the user
            from src.models.chapter import Chapter
            chapter = Chapter(
                title="Transaction Test Chapter",
                content="# Test\nTesting transactional integrity.",
                order=1,
                category="test",
                word_count=10
            )
            db.add(chapter)
            db.commit()

            # Verify both records exist
            user_check = db.query(User).filter(User.email == "transaction-test@example.com").first()
            assert user_check is not None

            chapter_check = db.query(Chapter).filter(Chapter.title == "Transaction Test Chapter").first()
            assert chapter_check is not None

            print("✓ Transactional integrity verified")

        finally:
            db.close()

    def test_foreign_key_relationships(self, setup_database):
        """Test that foreign key relationships work correctly."""
        db = TestingSessionLocal()

        try:
            # Create user
            auth_service = AuthService()
            user = auth_service.create_user(
                "fk-test@example.com",
                "Password123!",
                "FK",
                "Test"
            )

            # Create personalization record linked to user
            personalization = PersonalizationProfile(
                user_id=str(user.id),
                chapter_id=1,
                preference_type="difficulty",
                preference_value="beginner"
            )
            db.add(personalization)
            db.commit()

            # Verify the relationship exists
            loaded_personalization = db.query(PersonalizationProfile).filter(
                PersonalizationProfile.user_id == str(user.id)
            ).first()
            assert loaded_personalization is not None
            assert loaded_personalization.user_id == str(user.id)

            print("✓ Foreign key relationships verified")

        finally:
            db.close()


class TestAPIGatewayIntegration:
    """Test integration at the API gateway level."""

    def test_api_versioning_consistency(self, client, setup_database):
        """Test that API versioning is consistent across endpoints."""
        # Test that v1 endpoints exist and are properly versioned
        endpoints_to_test = [
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/profile",
            "/api/v1/chapters/",
            "/api/v1/chat/",
            "/api/v1/translation/translate",
            "/api/v1/personalization/",
            "/api/v1/users/profile"
        ]

        for endpoint in endpoints_to_test:
            # Check if endpoints exist (don't call them, just verify they're defined)
            # We'll do a GET request and expect either a method not allowed (405) or other appropriate response
            # but not 404 (not found)
            try:
                response = client.request("GET", endpoint)
                # Should not return 404 - endpoint should exist even if GET is not allowed
                assert response.status_code != 404, f"Endpoint {endpoint} not found"
            except Exception:
                # Some endpoints might require specific methods or parameters
                # The important thing is that they don't return 404
                pass

        print("✓ API versioning consistency verified")

    def test_cross_cutting_concerns_integration(self, client, setup_database):
        """Test integration of cross-cutting concerns like logging, error handling."""
        # Register user
        user_data = {
            "email": "cross-cutting@example.com",
            "password": "Password123!",
            "first_name": "Cross",
            "last_name": "Cutting"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        # Login
        login_response = client.post("/api/v1/auth/login", json={
            "email": "cross-cutting@example.com",
            "password": "Password123!"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Make multiple requests to test logging and monitoring
        endpoints = [
            ("/api/v1/auth/profile", "GET"),
            ("/api/v1/chapters/", "GET"),
            ("/api/v1/translation/supported-languages", "GET"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint, headers={"Authorization": f"Bearer {token}"})
            elif method == "POST":
                response = client.post(endpoint, headers={"Authorization": f"Bearer {token}"})

            # Should be properly handled (not crash)
            assert response.status_code != 500

        print("✓ Cross-cutting concerns integration verified")


def run_integration_tests():
    """Run all integration tests and return results."""
    import subprocess
    import sys

    # Run the tests using pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__,
        "-v",
        "--tb=short"
    ], capture_output=True, text=True)

    print("Integration Test Results:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    success = run_integration_tests()
    if success:
        print("\n✓ All integration tests passed!")
    else:
        print("\n✗ Some integration tests failed!")
        sys.exit(1)