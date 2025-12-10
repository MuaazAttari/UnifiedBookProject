from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum


class EducationalLevel(str, Enum):
    K12 = "K12"
    UNDERGRADUATE = "UNDERGRADUATE"
    GRADUATE = "GRADUATE"


class TextbookStatus(str, Enum):
    DRAFT = "DRAFT"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    REVIEWED = "REVIEWED"


class ChapterStatus(str, Enum):
    DRAFT = "DRAFT"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    REVIEWED = "REVIEWED"


class SectionType(str, Enum):
    CONTENT = "CONTENT"
    SUMMARY = "SUMMARY"
    EXERCISE = "EXERCISE"
    KEY_POINT = "KEY_POINT"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesResponse(BaseModel):
    id: str
    user_id: str
    default_educational_level: str
    default_format: str
    default_style: str
    include_exercises_by_default: bool
    include_summaries_by_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SectionResponse(BaseModel):
    id: str
    title: str
    content: str
    position: int
    created_at: datetime
    updated_at: datetime
    type: str
    chapter_id: str

    class Config:
        from_attributes = True


class ChapterResponse(BaseModel):
    id: str
    title: str
    content: Optional[str] = None
    position: int
    created_at: datetime
    updated_at: datetime
    status: str
    textbook_id: str
    sections: List[SectionResponse] = []

    class Config:
        from_attributes = True


class TextbookResponse(BaseModel):
    id: str
    title: str
    subject: str
    educational_level: str
    created_at: datetime
    updated_at: datetime
    status: str
    user_id: str
    settings: Optional[str] = None
    chapters: List[ChapterResponse] = []

    class Config:
        from_attributes = True


class TextbookGenerationRequest(BaseModel):
    subject: str
    title: str
    educational_level: str
    settings: Optional[dict] = {}


class TextbookGenerationResponse(BaseModel):
    id: str
    status: str
    created_at: str
    estimated_completion: Optional[str] = None


class UpdateChapterRequest(BaseModel):
    title: str
    content: str
    status: str


class UpdateChapterResponse(BaseModel):
    id: str
    title: str
    content: str
    status: str
    position: int
    updated_at: str


class UserPreferencesRequest(BaseModel):
    default_educational_level: str
    default_format: str
    default_style: str
    include_exercises_by_default: bool


class UserPreferencesResponseModel(BaseModel):
    default_educational_level: str
    default_format: str
    default_style: str
    include_exercises_by_default: bool
    include_summaries_by_default: bool
    updated_at: str