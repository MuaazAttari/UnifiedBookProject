from datetime import datetime
import uuid
from src.models.user import User
from src.models.textbook import Textbook


def test_user_model():
    """Test the User model"""
    user = User(
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.id is not None


def test_textbook_model():
    """Test the Textbook model"""
    textbook = Textbook(
        id=str(uuid.uuid4()),
        title="Test Textbook",
        subject="Test Subject",
        educational_level="UNDERGRADUATE",
        status="DRAFT",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    assert textbook.title == "Test Textbook"
    assert textbook.subject == "Test Subject"
    assert textbook.educational_level == "UNDERGRADUATE"
    assert textbook.status == "DRAFT"