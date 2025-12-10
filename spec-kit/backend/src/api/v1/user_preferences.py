from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from datetime import datetime, timedelta
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

from ...database.session import get_db
from ...models.user import User
from ...models.user_preferences import UserPreferences
from ...services.formatting import formatting_service
from ...models.api_responses import (
    UserPreferencesRequest,
    UserPreferencesResponseModel as UserPreferencesResponse
)

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.get("/user/preferences", response_model=UserPreferencesResponse)
@limiter.limit("20/minute")
async def get_user_preferences(db=Depends(get_db)):
    """
    Retrieve the current user's preferences for textbook generation.
    """
    # For now, using a temporary user ID - in real implementation this would come from authentication
    user_id = "temp-user-id"

    # Validate user_id format
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="User ID is required")

    # Get user preferences from the database
    user_preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

    if not user_preferences:
        # If no preferences exist, create default ones
        user_preferences = UserPreferences(
            user_id=user_id,
            default_educational_level="UNDERGRADUATE",
            default_format="PDF",
            default_style="academic",
            include_exercises_by_default=True,
            include_summaries_by_default=True
        )
        db.add(user_preferences)
        db.commit()
        db.refresh(user_preferences)

    return UserPreferencesResponse(
        default_educational_level=user_preferences.default_educational_level,
        default_format=user_preferences.default_format,
        default_style=user_preferences.default_style,
        include_exercises_by_default=user_preferences.include_exercises_by_default,
        include_summaries_by_default=user_preferences.include_summaries_by_default,
        updated_at=user_preferences.updated_at.isoformat() if user_preferences.updated_at else datetime.now().isoformat()
    )

@router.put("/user/preferences", response_model=UserPreferencesResponse)
@limiter.limit("10/minute")
async def update_user_preferences(request: UserPreferencesRequest, db=Depends(get_db)):
    """
    Update the current user's preferences for textbook generation.
    """
    # For now, using a temporary user ID - in real implementation this would come from authentication
    user_id = "temp-user-id"

    # Validate user_id format
    if not user_id or not user_id.strip():
        raise HTTPException(status_code=400, detail="User ID is required")

    # Validate input data
    valid_educational_levels = ["K12", "UNDERGRADUATE", "GRADUATE"]
    if request.default_educational_level not in valid_educational_levels:
        raise HTTPException(status_code=400, detail=f"Default educational level must be one of: {', '.join(valid_educational_levels)}")

    valid_formats = ["PDF", "DOCX", "HTML"]
    if request.default_format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Default format must be one of: {', '.join(valid_formats)}")

    valid_styles = ["academic", "casual", "technical"]
    if request.default_style not in valid_styles:
        raise HTTPException(status_code=400, detail=f"Default style must be one of: {', '.join(valid_styles)}")

    # Get existing user preferences or create new ones
    user_preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

    if not user_preferences:
        # Create new preferences if they don't exist
        user_preferences = UserPreferences(
            user_id=user_id,
            default_educational_level=request.default_educational_level,
            default_format=request.default_format,
            default_style=request.default_style,
            include_exercises_by_default=request.include_exercises_by_default,
            include_summaries_by_default=True  # Default value
        )
        db.add(user_preferences)
    else:
        # Update existing preferences
        user_preferences.default_educational_level = request.default_educational_level
        user_preferences.default_format = request.default_format
        user_preferences.default_style = request.default_style
        user_preferences.include_exercises_by_default = request.include_exercises_by_default
        user_preferences.include_summaries_by_default = True  # Default value

    db.commit()
    db.refresh(user_preferences)

    return UserPreferencesResponse(
        default_educational_level=user_preferences.default_educational_level,
        default_format=user_preferences.default_format,
        default_style=user_preferences.default_style,
        include_exercises_by_default=user_preferences.include_exercises_by_default,
        include_summaries_by_default=user_preferences.include_summaries_by_default,
        updated_at=user_preferences.updated_at.isoformat() if user_preferences.updated_at else datetime.now().isoformat()
    )

