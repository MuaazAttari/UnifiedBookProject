import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
import jwt

from src.main import app
from src.db.database import get_db
from src.config.settings import settings
from src.models.user import User


# Create a test database session
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
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


class TestAuthService:
    """Test suite for authentication service."""

    def test_register_user(self, client):
        """Test user registration."""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert "id" in data
        assert "hashed_password" not in data  # Should not return hashed password

    def test_register_user_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # Register first user
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        # Try to register with same email
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 409  # Conflict

    def test_login_user(self, client):
        """Test user login."""
        # First register a user
        user_data = {
            "email": "login@example.com",
            "password": "testpassword123",
            "first_name": "Login",
            "last_name": "User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        # Now login
        login_data = {
            "email": "login@example.com",
            "password": "testpassword123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify token is valid
        token = data["access_token"]
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "sub" in decoded
        assert "email" in decoded

    def test_login_user_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401  # Unauthorized

    def test_get_current_user(self, client):
        """Test getting current user with valid token."""
        # Register and login user
        user_data = {
            "email": "getuser@example.com",
            "password": "testpassword123",
            "first_name": "Get",
            "last_name": "User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "getuser@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Get current user
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "getuser@example.com"
        assert data["first_name"] == "Get"

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})

        assert response.status_code == 401  # Unauthorized

    def test_update_current_user(self, client):
        """Test updating current user information."""
        # Register and login user
        user_data = {
            "email": "update@example.com",
            "password": "testpassword123",
            "first_name": "Update",
            "last_name": "User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "update@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Update user
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "software_experience": "intermediate"
        }

        response = client.put("/api/v1/auth/me",
                             json=update_data,
                             headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["software_experience"] == "intermediate"

    def test_save_background_questionnaire(self, client):
        """Test saving user background questionnaire."""
        # Register and login user
        user_data = {
            "email": "questionnaire@example.com",
            "password": "testpassword123",
            "first_name": "Questionnaire",
            "last_name": "User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "questionnaire@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Save questionnaire
        questionnaire_data = {
            "education_level": "graduate",
            "technical_background": "Software engineering background",
            "learning_goals": "Learn about AI and robotics",
            "preferred_learning_style": "hands_on",
            "experience_with_ai": "intermediate",
            "experience_with_robotics": "beginner",
            "timezone": "GMT+5",
            "additional_notes": "Looking forward to hands-on projects"
        }

        response = client.post("/api/v1/auth/questionnaire",
                              json=questionnaire_data,
                              headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["education_level"] == "graduate"
        assert data["technical_background"] == "Software engineering background"
        assert data["user_id"] is not None

    def test_get_background_questionnaire(self, client):
        """Test getting user background questionnaire."""
        # Register and login user
        user_data = {
            "email": "getquestionnaire@example.com",
            "password": "testpassword123",
            "first_name": "Get",
            "last_name": "Questionnaire"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "getquestionnaire@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # First save questionnaire
        questionnaire_data = {
            "education_level": "undergraduate",
            "technical_background": "Computer science student",
            "learning_goals": "Master AI concepts",
        }

        response = client.post("/api/v1/auth/questionnaire",
                              json=questionnaire_data,
                              headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

        # Now get questionnaire
        response = client.get("/api/v1/auth/questionnaire",
                             headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["education_level"] == "undergraduate"
        assert data["technical_background"] == "Computer science student"

    def test_check_questionnaire_exists(self, client):
        """Test checking if questionnaire exists."""
        # Register and login user
        user_data = {
            "email": "checkexists@example.com",
            "password": "testpassword123",
            "first_name": "Check",
            "last_name": "Exists"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200

        login_data = {
            "email": "checkexists@example.com",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Check if questionnaire exists (should be false initially)
        response = client.get("/api/v1/auth/questionnaire/exists",
                             headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()["exists"] is False

        # Now save a questionnaire
        questionnaire_data = {
            "education_level": "high_school",
        }

        response = client.post("/api/v1/auth/questionnaire",
                              json=questionnaire_data,
                              headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

        # Check again (should be true now)
        response = client.get("/api/v1/auth/questionnaire/exists",
                             headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json()["exists"] is True


class TestAuthUtilities:
    """Test suite for authentication utilities."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        from src.utils.auth import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        # Verify the password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_jwt_token_creation(self):
        """Test JWT token creation and decoding."""
        from src.utils.auth import create_access_token, decode_access_token

        data = {"sub": "test_user_id", "email": "test@example.com"}
        token = create_access_token(data)

        # Decode the token
        decoded = decode_access_token(token)
        assert decoded["sub"] == "test_user_id"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded