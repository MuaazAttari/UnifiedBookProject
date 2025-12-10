# Import all models to register them with SQLAlchemy Base
from ..models.user import User
from ..models.user_preferences import UserPreferences
from ..models.textbook import Textbook
from ..models.chapter import Chapter
from ..models.section import Section

# Ensure relationships are properly set up
from ..models.user_preferences import User  # This will set up the relationship
from ..models.textbook import User  # This will set up the relationship
from ..models.chapter import Textbook  # This will set up the relationship
from ..models.section import Chapter  # This will set up the relationship