from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user creation."""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for user updates."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    software_experience: Optional[str] = None  # beginner, intermediate, expert
    hardware_availability: Optional[str] = None
    robotics_familiarity: Optional[str] = None  # beginner, intermediate, expert


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    software_experience: Optional[str] = None
    hardware_availability: Optional[str] = None
    robotics_familiarity: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"


class BackgroundQuestionnaire(BaseModel):
    """Schema for user background questionnaire."""
    education_level: Optional[str] = None  # e.g., "high_school", "undergraduate", "graduate", "professional"
    technical_background: Optional[str] = None  # Free text about technical experience
    learning_goals: Optional[str] = None  # What the user wants to learn
    preferred_learning_style: Optional[str] = None  # e.g., "visual", "hands_on", "theoretical"
    experience_with_ai: Optional[str] = None  # e.g., "beginner", "intermediate", "advanced"
    experience_with_robotics: Optional[str] = None  # e.g., "beginner", "intermediate", "advanced"
    timezone: Optional[str] = None  # User's timezone
    additional_notes: Optional[str] = None  # Any additional information


class BackgroundQuestionnaireResponse(BaseModel):
    """Schema for background questionnaire response."""
    id: str
    user_id: str
    education_level: Optional[str] = None
    technical_background: Optional[str] = None
    learning_goals: Optional[str] = None
    preferred_learning_style: Optional[str] = None
    experience_with_ai: Optional[str] = None
    experience_with_robotics: Optional[str] = None
    timezone: Optional[str] = None
    additional_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True