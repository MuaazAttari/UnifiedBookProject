from typing import Optional
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.user import User, UserBackgroundQuestionnaire
from src.utils.auth import verify_password, get_password_hash, create_access_token
from src.schemas.auth import UserCreate, UserUpdate, UserResponse, BackgroundQuestionnaire


class AuthService:
    """Service class for authentication functionality."""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User's email address
            password: Plain text password

        Returns:
            User object if authentication is successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """
        Create an access token for a user.

        Args:
            user: User object

        Returns:
            JWT access token string
        """
        access_token_expires = timedelta(minutes=30)  # 30 minutes expiry
        return create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created User object

        Raises:
            HTTPException: If email already exists
        """
        # Check if user with this email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists"
            )

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create the user
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )

        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists"
            )

        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get a user by their email.

        Args:
            db: Database session
            email: User email

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        Update user information.

        Args:
            db: Database session
            user_id: User ID
            user_data: User update data

        Returns:
            Updated User object or None if user not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        # Update fields if provided
        if user_data.first_name is not None:
            db_user.first_name = user_data.first_name
        if user_data.last_name is not None:
            db_user.last_name = user_data.last_name
        if user_data.software_experience is not None:
            db_user.software_experience = user_data.software_experience
        if user_data.hardware_availability is not None:
            db_user.hardware_availability = user_data.hardware_availability
        if user_data.robotics_familiarity is not None:
            db_user.robotics_familiarity = user_data.robotics_familiarity

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def set_user_verified(db: Session, user_id: str) -> Optional[User]:
        """
        Mark a user as verified.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Updated User object or None if user not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        db_user.is_verified = True
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def save_user_background_questionnaire(
        db: Session,
        user_id: str,
        questionnaire_data: BackgroundQuestionnaire
    ) -> UserBackgroundQuestionnaire:
        """
        Save user background questionnaire responses.

        Args:
            db: Database session
            user_id: User ID
            questionnaire_data: Questionnaire data

        Returns:
            Created UserBackgroundQuestionnaire object
        """
        # Check if questionnaire already exists for this user
        existing_questionnaire = db.query(UserBackgroundQuestionnaire).filter(
            UserBackgroundQuestionnaire.user_id == user_id
        ).first()

        if existing_questionnaire:
            # Update existing questionnaire
            for field, value in questionnaire_data.dict(exclude_unset=True).items():
                setattr(existing_questionnaire, field, value)
            db.commit()
            db.refresh(existing_questionnaire)
            return existing_questionnaire
        else:
            # Create new questionnaire
            db_questionnaire = UserBackgroundQuestionnaire(
                user_id=user_id,
                education_level=questionnaire_data.education_level,
                technical_background=questionnaire_data.technical_background,
                learning_goals=questionnaire_data.learning_goals,
                preferred_learning_style=questionnaire_data.preferred_learning_style,
                experience_with_ai=questionnaire_data.experience_with_ai,
                experience_with_robotics=questionnaire_data.experience_with_robotics,
                timezone=questionnaire_data.timezone,
                additional_notes=questionnaire_data.additional_notes
            )

            db.add(db_questionnaire)
            db.commit()
            db.refresh(db_questionnaire)
            return db_questionnaire

    @staticmethod
    def get_user_background_questionnaire(db: Session, user_id: str) -> Optional[UserBackgroundQuestionnaire]:
        """
        Get user background questionnaire responses.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            UserBackgroundQuestionnaire object or None if not found
        """
        return db.query(UserBackgroundQuestionnaire).filter(
            UserBackgroundQuestionnaire.user_id == user_id
        ).first()