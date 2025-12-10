from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class PersonalizationProfileCreate(BaseModel):
    """Schema for creating a personalization profile."""
    difficulty_level: Optional[str] = None  # beginner, intermediate, expert
    content_preferences: Optional[Dict[str, Any]] = None  # e.g., {"diagrams": True, "examples": True}
    learning_style: Optional[str] = None  # visual, hands_on, theoretical
    personalization_enabled: bool = False
    custom_preferences: Optional[Dict[str, Any]] = None  # Additional custom preferences


class PersonalizationProfileUpdate(BaseModel):
    """Schema for updating a personalization profile."""
    difficulty_level: Optional[str] = None
    content_preferences: Optional[Dict[str, Any]] = None
    learning_style: Optional[str] = None
    personalization_enabled: Optional[bool] = None
    custom_preferences: Optional[Dict[str, Any]] = None


class PersonalizationProfileResponse(BaseModel):
    """Schema for personalization profile response."""
    id: str
    user_id: str
    chapter_id: str
    difficulty_level: Optional[str] = None
    content_preferences: Optional[Dict[str, Any]] = None
    learning_style: Optional[str] = None
    personalization_enabled: bool
    custom_preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonalizationAdjustmentRequest(BaseModel):
    """Schema for requesting content personalization."""
    content: str
    chapter_id: str
    difficulty_level: Optional[str] = None  # Can override user's default
    learning_style: Optional[str] = None  # Can override user's default


class PersonalizationAdjustmentResponse(BaseModel):
    """Schema for content personalization response."""
    original_content: str
    adjusted_content: str
    personalization_applied: bool
    personalization_settings: Dict[str, Any]


class PersonalizationSettingsResponse(BaseModel):
    """Schema for user's personalization settings."""
    difficulty_level: str
    content_preferences: Dict[str, Any]
    learning_style: str
    personalization_enabled: bool
    custom_preferences: Dict[str, Any]