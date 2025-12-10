from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlalchemy import func
from slowapi import Limiter
from slowapi.util import get_remote_address

from ...database.session import get_db
from ...models.chapter import Chapter
from ...models.section import Section
from ...services.textbook_generation import textbook_generation_service
from ...models.api_responses import UpdateChapterRequest, UpdateChapterResponse

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.put("/chapter/{chapter_id}", response_model=UpdateChapterResponse)
@limiter.limit("10/minute")
async def update_chapter(chapter_id: str, request: UpdateChapterRequest, db=Depends(get_db)):
    """
    Update the content of a specific chapter after review.
    """
    import re

    # Validate chapter_id format
    if not re.match(r'^[a-zA-Z0-9-]+$', chapter_id):
        raise HTTPException(status_code=400, detail="Invalid chapter ID format")

    # Validate input data
    if not request.title or len(request.title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    if len(request.title) > 200:
        raise HTTPException(status_code=400, detail="Title cannot exceed 200 characters")

    if not request.content or len(request.content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Content is required and cannot be empty")

    if len(request.content) > 10000:  # Limit content to 10k characters
        raise HTTPException(status_code=400, detail="Content cannot exceed 10000 characters")

    valid_statuses = ["DRAFT", "GENERATING", "COMPLETED", "REVIEWED"]
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(valid_statuses)}")

    # Sanitize inputs
    sanitized_title = request.title.strip()
    sanitized_content = request.content.strip()

    # Get the chapter
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Update the chapter
    chapter.title = sanitized_title
    chapter.status = request.status
    db.add(chapter)

    # Update the first section's content (in a real implementation,
    # we might want to update multiple sections or create new ones)
    section = db.query(Section).filter(Section.chapter_id == chapter_id).first()
    if section:
        section.content = sanitized_content
        db.add(section)
    else:
        # If no section exists, create one
        new_section = Section(
            title=sanitized_title,
            content=sanitized_content,
            position=1,
            type="CONTENT",
            chapter_id=chapter_id
        )
        db.add(new_section)

    db.commit()

    return UpdateChapterResponse(
        id=chapter.id,
        title=chapter.title,
        content=sanitized_content,
        status=chapter.status,
        position=chapter.position,
        updated_at=chapter.updated_at.isoformat() if chapter.updated_at else datetime.now().isoformat()
    )


@router.put("/section/{section_id}")
@limiter.limit("15/minute")
async def update_section(section_id: str, title: str = None, content: str = None, type: str = None, db=Depends(get_db)):
    """
    Update the content of a specific section after review.
    """
    import re

    # Validate section_id format
    if not re.match(r'^[a-zA-Z0-9-]+$', section_id):
        raise HTTPException(status_code=400, detail="Invalid section ID format")

    # Validate and sanitize inputs if provided
    if title is not None:
        if len(title.strip()) == 0:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        if len(title) > 200:
            raise HTTPException(status_code=400, detail="Title cannot exceed 200 characters")
        title = title.strip()

    if content is not None:
        if len(content) > 10000:  # Limit content to 10k characters
            raise HTTPException(status_code=400, detail="Content cannot exceed 10000 characters")
        content = content.strip()

    if type is not None:
        valid_types = ["CONTENT", "SUMMARY", "EXERCISE", "KEY_POINT"]
        if type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Type must be one of: {', '.join(valid_types)}")

    # Get the section
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    # Update the section fields if provided
    if title is not None:
        section.title = title
    if content is not None:
        section.content = content
    if type is not None:
        section.type = type

    db.add(section)
    db.commit()

    return {
        "id": section.id,
        "title": section.title,
        "content": section.content,
        "type": section.type,
        "position": section.position,
        "updated_at": section.updated_at.isoformat() if section.updated_at else datetime.now().isoformat()
    }


@router.post("/chapter/{chapter_id}/section")
@limiter.limit("10/minute")
async def add_section(chapter_id: str, title: str, content: str, type: str = "CONTENT", position: int = None, db=Depends(get_db)):
    """
    Add a new section to a chapter.
    """
    import re

    # Validate chapter_id format
    if not re.match(r'^[a-zA-Z0-9-]+$', chapter_id):
        raise HTTPException(status_code=400, detail="Invalid chapter ID format")

    # Validate input data
    if not title or len(title.strip()) == 0:
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    if len(title) > 200:
        raise HTTPException(status_code=400, detail="Title cannot exceed 200 characters")

    if not content or len(content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Content is required and cannot be empty")

    if len(content) > 10000:  # Limit content to 10k characters
        raise HTTPException(status_code=400, detail="Content cannot exceed 10000 characters")

    valid_types = ["CONTENT", "SUMMARY", "EXERCISE", "KEY_POINT"]
    if type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Type must be one of: {', '.join(valid_types)}")

    if position is not None and position < 1:
        raise HTTPException(status_code=400, detail="Position must be a positive integer")

    # Sanitize inputs
    sanitized_title = title.strip()
    sanitized_content = content.strip()

    # Verify the chapter exists
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Determine position if not provided
    if position is None:
        max_position = db.query(func.coalesce(func.max(Section.position), 0)).filter(Section.chapter_id == chapter_id).scalar()
        position = max_position + 1

    # Create the new section
    new_section = Section(
        title=sanitized_title,
        content=sanitized_content,
        position=position,
        type=type,
        chapter_id=chapter_id
    )

    db.add(new_section)
    db.commit()

    return {
        "id": new_section.id,
        "title": new_section.title,
        "content": new_section.content,
        "type": new_section.type,
        "position": new_section.position,
        "chapter_id": new_section.chapter_id,
        "created_at": new_section.created_at.isoformat() if new_section.created_at else datetime.now().isoformat()
    }


@router.delete("/section/{section_id}")
@limiter.limit("10/minute")
async def delete_section(section_id: str, db=Depends(get_db)):
    """
    Delete a section from a chapter.
    """
    import re

    # Validate section_id format
    if not re.match(r'^[a-zA-Z0-9-]+$', section_id):
        raise HTTPException(status_code=400, detail="Invalid section ID format")

    # Get the section
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    db.delete(section)
    db.commit()

    return {"message": "Section deleted successfully"}

@router.post("/improve-content/{content_id}")
@limiter.limit("5/minute")
async def improve_content(content_id: str, content_type: str, feedback: str, educational_level: str, db=Depends(get_db)):
    """
    Improve content based on user feedback using AI.
    """
    import re

    # Validate content_id format
    if not re.match(r'^[a-zA-Z0-9-]+$', content_id):
        raise HTTPException(status_code=400, detail="Invalid content ID format")

    # Validate content_type
    valid_content_types = ["chapter", "section"]
    if content_type.lower() not in valid_content_types:
        raise HTTPException(status_code=400, detail=f"Content type must be one of: {', '.join(valid_content_types)}")

    # Validate feedback
    if not feedback or len(feedback.strip()) == 0:
        raise HTTPException(status_code=400, detail="Feedback is required and cannot be empty")

    if len(feedback) > 2000:  # Limit feedback to 2k characters
        raise HTTPException(status_code=400, detail="Feedback cannot exceed 2000 characters")

    # Validate educational level
    valid_levels = ["K12", "UNDERGRADUATE", "GRADUATE"]
    if educational_level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"Educational level must be one of: {', '.join(valid_levels)}")

    # Sanitize feedback
    sanitized_feedback = feedback.strip()

    try:
        improved_content = await textbook_generation_service.update_content_with_feedback(
            db=db,
            content_id=content_id,
            content_type=content_type,
            feedback=sanitized_feedback,
            educational_level=educational_level
        )

        return {"improved_content": improved_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error improving content: {str(e)}")