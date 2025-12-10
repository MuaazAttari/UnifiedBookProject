from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional

from src.db.database import get_db
from src.services.auth_service import AuthService
from src.schemas.auth import UserCreate, UserResponse, UserLogin, TokenResponse, BackgroundQuestionnaire, BackgroundQuestionnaireResponse
from src.utils.auth import security
from src.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    # Create the user
    try:
        db_user = AuthService.create_user(db, user_data)
        return db_user
    except HTTPException:
        # Re-raise HTTP exceptions (like email already exists)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token.
    """
    user = AuthService.authenticate_user(
        db,
        email=login_data.email,
        password=login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login time
    user.last_login_at = func.now()
    db.commit()

    # Create access token
    access_token = AuthService.create_access_token_for_user(user)

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    """
    # Get user from database
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    """
    # Update user
    updated_user = AuthService.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


@router.post("/questionnaire", response_model=BackgroundQuestionnaireResponse)
def save_background_questionnaire(
    questionnaire_data: BackgroundQuestionnaire,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Save user background questionnaire responses.
    """
    # Save questionnaire
    questionnaire = AuthService.save_user_background_questionnaire(
        db, user_id, questionnaire_data
    )

    return questionnaire


@router.get("/questionnaire", response_model=BackgroundQuestionnaireResponse)
def get_background_questionnaire(
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get user background questionnaire responses.
    """
    # Get questionnaire
    questionnaire = AuthService.get_user_background_questionnaire(db, user_id)
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )

    return questionnaire


@router.get("/questionnaire/exists")
def check_questionnaire_exists(
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Check if user has completed the background questionnaire.
    """
    # Check if questionnaire exists
    questionnaire = AuthService.get_user_background_questionnaire(db, user_id)
    return {"exists": questionnaire is not None}


# Import func here to avoid circular import issues
from sqlalchemy.sql import func