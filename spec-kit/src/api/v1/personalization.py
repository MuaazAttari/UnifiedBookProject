from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.services.personalization_service import PersonalizationService
from src.schemas.personalization import (
    PersonalizationProfileCreate, PersonalizationProfileUpdate,
    PersonalizationProfileResponse, PersonalizationAdjustmentRequest,
    PersonalizationAdjustmentResponse, PersonalizationSettingsResponse
)
from src.utils.auth import get_current_user_id_from_token
from src.services.chapter_service import ChapterService

router = APIRouter()


@router.post("/", response_model=PersonalizationProfileResponse)
def create_personalization_profile(
    profile_data: PersonalizationProfileCreate,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Create a personalization profile for a chapter.
    """
    # Verify that the chapter exists
    # Note: We don't have a direct chapter validation here, but in a real implementation
    # we would validate that the chapter_id exists

    # For now, we'll use a placeholder chapter_id from the request
    # In a real implementation, you'd get this from the path or another source
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="This endpoint requires a chapter_id parameter. Use /chapters/{chapter_id}/profile instead."
    )


@router.post("/chapters/{chapter_id}", response_model=PersonalizationProfileResponse)
def create_chapter_personalization_profile(
    chapter_id: str,
    profile_data: PersonalizationProfileCreate,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Create a personalization profile for a specific chapter.
    """
    # Verify that the chapter exists
    chapter = ChapterService.get_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id {chapter_id} not found"
        )

    # Create the personalization profile
    profile = PersonalizationService.create_personalization_profile(
        db, user_id, chapter_id, profile_data
    )

    return profile


@router.get("/chapters/{chapter_id}", response_model=PersonalizationProfileResponse)
def get_chapter_personalization_profile(
    chapter_id: str,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get personalization profile for a specific chapter.
    """
    profile = PersonalizationService.get_personalization_profile(db, user_id, chapter_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personalization profile not found for this chapter"
        )

    return profile


@router.put("/chapters/{chapter_id}", response_model=PersonalizationProfileResponse)
def update_chapter_personalization_profile(
    chapter_id: str,
    profile_data: PersonalizationProfileUpdate,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Update personalization profile for a specific chapter.
    """
    profile = PersonalizationService.update_personalization_profile(
        db, user_id, chapter_id, profile_data
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personalization profile not found for this chapter"
        )

    return profile


@router.delete("/chapters/{chapter_id}")
def delete_chapter_personalization_profile(
    chapter_id: str,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Delete personalization profile for a specific chapter.
    """
    deleted = PersonalizationService.delete_personalization_profile(db, user_id, chapter_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personalization profile not found for this chapter"
        )

    return {"message": "Personalization profile deleted successfully"}


@router.get("/settings", response_model=PersonalizationSettingsResponse)
def get_user_personalization_settings(
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get user's overall personalization settings (defaults for all chapters).
    """
    # For now, return default settings
    # In a real implementation, we might aggregate user's personalization preferences
    # or get them from their questionnaire

    # Get user's questionnaire to determine default settings
    from src.services.auth_service import AuthService
    questionnaire = AuthService.get_user_background_questionnaire(db, user_id)

    if questionnaire:
        difficulty_level = questionnaire.experience_with_ai or questionnaire.experience_with_robotics or "intermediate"
        learning_style = questionnaire.preferred_learning_style or "theoretical"
    else:
        difficulty_level = "intermediate"
        learning_style = "theoretical"

    return PersonalizationSettingsResponse(
        difficulty_level=difficulty_level,
        content_preferences={"diagrams": True, "examples": True},
        learning_style=learning_style,
        personalization_enabled=True,
        custom_preferences={}
    )


@router.post("/adjust-content", response_model=PersonalizationAdjustmentResponse)
def adjust_content(
    request: PersonalizationAdjustmentRequest,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Adjust content based on user's personalization preferences.
    """
    # Get personalization settings for this specific chapter
    personalization_settings = PersonalizationService.get_user_personalization_for_chapter(
        db, user_id, request.chapter_id
    )

    # Apply personalization to content
    adjusted_content = PersonalizationService.adjust_content_for_user(
        db, request.content, user_id, request.chapter_id
    )

    return PersonalizationAdjustmentResponse(
        original_content=request.content,
        adjusted_content=adjusted_content,
        personalization_applied=personalization_settings.get("personalization_enabled", False),
        personalization_settings=personalization_settings
    )


@router.get("/chapters/{chapter_id}/settings", response_model=PersonalizationSettingsResponse)
def get_chapter_personalization_settings(
    chapter_id: str,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get personalization settings for a specific chapter.
    """
    settings = PersonalizationService.get_user_personalization_for_chapter(
        db, user_id, chapter_id
    )

    return PersonalizationSettingsResponse(
        difficulty_level=settings.get("difficulty_level", "intermediate"),
        content_preferences=settings.get("content_preferences", {}),
        learning_style=settings.get("learning_style", "theoretical"),
        personalization_enabled=settings.get("personalization_enabled", False),
        custom_preferences=settings.get("custom_preferences", {})
    )


@router.get("/my-profiles")
def get_user_profiles(
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get all personalization profiles for the current user.
    """
    profiles = PersonalizationService.get_all_user_profiles(db, user_id)
    return [
        {
            "id": profile.id,
            "chapter_id": profile.chapter_id,
            "difficulty_level": profile.difficulty_level,
            "learning_style": profile.learning_style,
            "personalization_enabled": profile.personalization_enabled,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }
        for profile in profiles
    ]