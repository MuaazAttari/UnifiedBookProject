from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime
import uuid
from fastapi.background import BackgroundTasks
from slowapi import Limiter
from slowapi.util import get_remote_address

from ...database.session import get_db
from ...models.textbook import Textbook
from ...services.textbook_generation import textbook_generation_service
from ...models.api_responses import (
    TextbookGenerationRequest,
    TextbookGenerationResponse as TextbookGenerationResponseModel,
    TextbookResponse,
    ChapterResponse,
    SectionResponse
)

# Initialize rate limiter for this router
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/textbook/generate", response_model=TextbookGenerationResponseModel)
@limiter.limit("5/minute")
async def create_textbook(request: TextbookGenerationRequest, background_tasks: BackgroundTasks, db=Depends(get_db)):
    """
    Initiate the generation of a new textbook based on the provided parameters.
    """
    from ...utils.logging_config import get_logger
    logger = get_logger(__name__)

    try:
        # Input validation
        if not request.title or len(request.title.strip()) == 0:
            logger.warning(f"Invalid request: Title is required and cannot be empty")
            raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

        if len(request.title) > 200:
            logger.warning(f"Invalid request: Title exceeds 200 characters")
            raise HTTPException(status_code=400, detail="Title cannot exceed 200 characters")

        if not request.subject or len(request.subject.strip()) == 0:
            logger.warning(f"Invalid request: Subject is required and cannot be empty")
            raise HTTPException(status_code=400, detail="Subject is required and cannot be empty")

        if len(request.subject) > 200:
            logger.warning(f"Invalid request: Subject exceeds 200 characters")
            raise HTTPException(status_code=400, detail="Subject cannot exceed 200 characters")

        valid_educational_levels = ["K12", "UNDERGRADUATE", "GRADUATE"]
        if request.educational_level not in valid_educational_levels:
            logger.warning(f"Invalid educational level: {request.educational_level}")
            raise HTTPException(status_code=400, detail=f"Educational level must be one of: {', '.join(valid_educational_levels)}")

        # Sanitize inputs
        sanitized_title = request.title.strip()
        sanitized_subject = request.subject.strip()

        logger.info(f"Creating textbook with title: {sanitized_title}, subject: {sanitized_subject}")

        # Load user preferences to apply default settings
        from ...models.user_preferences import UserPreferences as UserPreferencesModel
        user_id = "temp-user-id"  # This would come from authentication
        user_preferences = db.query(UserPreferencesModel).filter(UserPreferencesModel.user_id == user_id).first()

        # Create the textbook record first
        from ...models.textbook import Textbook as TextbookModel
        textbook = TextbookModel(
            title=sanitized_title,
            subject=sanitized_subject,
            educational_level=request.educational_level,
            status="PENDING",  # Changed from GENERATING to PENDING for initial state
            user_id=user_id,  # This would come from authentication
            settings=str(request.settings)
        )
        db.add(textbook)
        db.commit()
        db.refresh(textbook)

        # Prepare settings that combine request parameters with user preferences
        final_settings = request.settings or {}

        # Apply user preferences if available
        if user_preferences:
            # Override with user's default educational level if not specified in request
            if not request.educational_level:
                request.educational_level = user_preferences.default_educational_level
            # Add preferences to settings
            final_settings.update({
                'default_format': user_preferences.default_format,
                'default_style': user_preferences.default_style,
                'include_exercises': user_preferences.include_exercises_by_default,
                'include_summaries': user_preferences.include_summaries_by_default
            })

        # Add the background task to generate the textbook content
        background_tasks.add_task(
            textbook_generation_service.generate_textbook_background,
            db,
            textbook.id,
            sanitized_subject,
            sanitized_title,
            request.educational_level,
            final_settings
        )

        logger.info(f"Successfully initiated textbook generation with ID: {textbook.id}")

        return TextbookGenerationResponseModel(
            id=textbook.id,
            status=textbook.status,
            created_at=textbook.created_at.isoformat() if textbook.created_at else datetime.now().isoformat(),
            estimated_completion=(datetime.now().replace(minute=datetime.now().minute + 5)).isoformat() if textbook.status == "PENDING" else None
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        logger.warning(f"HTTP exception during textbook generation: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error initiating textbook generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error initiating textbook generation: {str(e)}")

@router.get("/textbook/{textbook_id}", response_model=TextbookResponse)
@limiter.limit("20/minute")
async def get_textbook(textbook_id: str, db=Depends(get_db)):
    """
    Retrieve the current status and details of a textbook generation process.
    """
    from ...models.chapter import Chapter
    from ...models.section import Section
    from sqlalchemy import asc

    # Get the textbook
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")

    # Get chapters for this textbook
    chapters = db.query(Chapter).filter(Chapter.textbook_id == textbook_id).order_by(asc(Chapter.position)).all()

    chapters_list = []
    for chapter in chapters:
        sections = db.query(Section).filter(Section.chapter_id == chapter.id).order_by(asc(Section.position)).all()

        sections_list = []
        for section in sections:
            section_response = {
                "id": section.id,
                "title": section.title,
                "content": section.content,
                "position": section.position,
                "created_at": section.created_at,
                "updated_at": section.updated_at,
                "type": section.type,
                "chapter_id": section.chapter_id
            }
            sections_list.append(SectionResponse(**section_response))

        chapter_response = {
            "id": chapter.id,
            "title": chapter.title,
            "position": chapter.position,
            "created_at": chapter.created_at,
            "updated_at": chapter.updated_at,
            "status": chapter.status,
            "textbook_id": chapter.textbook_id,
            "sections": sections_list
        }
        chapters_list.append(ChapterResponse(**chapter_response))

    textbook_response = {
        "id": textbook.id,
        "title": textbook.title,
        "subject": textbook.subject,
        "educational_level": textbook.educational_level,
        "created_at": textbook.created_at,
        "updated_at": textbook.updated_at,
        "status": textbook.status,
        "user_id": textbook.user_id,
        "settings": textbook.settings,
        "chapters": chapters_list
    }

    return TextbookResponse(**textbook_response)


@router.post("/textbook/{textbook_id}/export")
@limiter.limit("10/minute")
async def export_textbook(textbook_id: str, format: str = "pdf", include_solutions: bool = False, db=Depends(get_db)):
    """
    Export the textbook in the specified format.
    """
    from ...services.formatting import formatting_service
    from datetime import datetime, timedelta
    import os
    import re

    # Validate textbook_id format (simple UUID validation)
    if not re.match(r'^[a-zA-Z0-9-]+$', textbook_id):
        raise HTTPException(status_code=400, detail="Invalid textbook ID format")

    # Validate format
    valid_formats = ["pdf", "docx", "html"]
    if format.lower() not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Supported formats: {', '.join(valid_formats)}")

    # Get the textbook
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")

    if textbook.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Textbook must be completed before export")

    try:
        if format.lower() == "pdf":
            file_path = formatting_service.export_to_pdf(db, textbook_id, include_solutions)
            return {
                "download_url": f"/api/v1/download/{os.path.basename(file_path)}",
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
                "format": "pdf"
            }
        elif format.lower() == "docx":
            file_path = formatting_service.export_to_docx(db, textbook_id, include_solutions)
            return {
                "download_url": f"/api/v1/download/{os.path.basename(file_path)}",
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
                "format": "docx"
            }
        elif format.lower() == "html":
            file_path = formatting_service.export_to_html(db, textbook_id, include_solutions)
            return {
                "download_url": f"/api/v1/download/{os.path.basename(file_path)}",
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
                "format": "html"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Supported formats: pdf, docx, html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting textbook: {str(e)}")


# Add a download endpoint for exported files
@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download an exported textbook file.
    NOTE: In production, implement proper security and file cleanup.
    """
    import os
    from fastapi.responses import FileResponse
    import tempfile

    # Construct the file path using the temporary directory
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type='application/octet-stream', filename=filename)