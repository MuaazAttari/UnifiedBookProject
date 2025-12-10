import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.textbook import Textbook
from ..models.chapter import Chapter
from ..models.section import Section
from .content_generation import content_generation_service


class TextbookGenerationService:
    """
    Service for managing the textbook generation process
    """

    async def generate_textbook(
        self,
        db: Session,
        subject: str,
        title: str,
        educational_level: str,
        user_id: str,
        settings: Optional[Dict] = None
    ) -> Textbook:
        """
        Generate a complete textbook with chapters and sections
        """
        if settings is None:
            settings = {}

        # Create the textbook record
        textbook = Textbook(
            title=title,
            subject=subject,
            educational_level=educational_level,
            status="GENERATING",
            user_id=user_id,
            settings=str(settings)
        )
        db.add(textbook)
        db.commit()
        db.refresh(textbook)

        try:
            # Generate the textbook outline
            outline = await content_generation_service.generate_textbook_outline(
                subject=subject,
                educational_level=educational_level,
                chapters_count=settings.get("chapters_count", 10),
                settings=settings
            )

            # Update textbook title if it was generated
            if outline.get("title"):
                textbook.title = outline["title"]

            # Create chapters and sections based on the outline
            for chapter_data in outline.get("chapters", []):
                chapter = Chapter(
                    title=chapter_data["title"],
                    position=chapter_data["position"],
                    status="GENERATING",
                    textbook_id=textbook.id
                )
                db.add(chapter)
                db.flush()  # Get the chapter ID without committing

                # Create sections for this chapter
                for section_data in chapter_data.get("sections", []):
                    section = Section(
                        title=section_data["title"],
                        content=section_data["content"],
                        position=section_data["position"],
                        type=section_data["type"],
                        chapter_id=chapter.id
                    )
                    db.add(section)

                # Update chapter status to completed after sections are created
                chapter.status = "COMPLETED"
                db.add(chapter)

            # Update textbook status to completed
            textbook.status = "COMPLETED"
            db.add(textbook)
            db.commit()

            return textbook

        except Exception as e:
            # If there's an error, mark the textbook as failed
            textbook.status = "FAILED"
            db.add(textbook)
            db.commit()
            raise e

    async def generate_textbook_background(
        self,
        db: Session,
        textbook_id: str,
        subject: str,
        title: str,
        educational_level: str,
        settings: Optional[Dict] = None
    ):
        """
        Background task to generate textbook content asynchronously
        """
        if settings is None:
            settings = {}

        try:
            # Get the textbook record
            textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
            if not textbook:
                raise ValueError(f"Textbook with id {textbook_id} not found")

            # Update status to GENERATING
            textbook.status = "GENERATING"
            db.add(textbook)
            db.commit()

            # Generate the textbook outline
            outline = await content_generation_service.generate_textbook_outline(
                subject=subject,
                educational_level=educational_level,
                chapters_count=settings.get("chapters_count", 10),
                settings=settings
            )

            # Update textbook title if it was generated
            if outline.get("title"):
                textbook.title = outline["title"]

            # Create chapters and sections based on the outline
            for chapter_data in outline.get("chapters", []):
                chapter = Chapter(
                    title=chapter_data["title"],
                    position=chapter_data["position"],
                    status="GENERATING",
                    textbook_id=textbook.id
                )
                db.add(chapter)
                db.flush()  # Get the chapter ID without committing

                # Create sections for this chapter
                for section_data in chapter_data.get("sections", []):
                    section = Section(
                        title=section_data["title"],
                        content=section_data["content"],
                        position=section_data["position"],
                        type=section_data["type"],
                        chapter_id=chapter.id
                    )
                    db.add(section)

                # Update chapter status to completed after sections are created
                chapter.status = "COMPLETED"
                db.add(chapter)

            # Update textbook status to completed
            textbook.status = "COMPLETED"
            db.add(textbook)
            db.commit()

        except Exception as e:
            # If there's an error, mark the textbook as failed
            textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
            if textbook:
                textbook.status = "FAILED"
                db.add(textbook)
                db.commit()
            print(f"Error in background textbook generation: {str(e)}")
            raise e

    async def generate_chapter(
        self,
        db: Session,
        textbook_id: str,
        chapter_title: str,
        position: int,
        educational_level: str,
        include_exercises: bool = True,
        include_summaries: bool = True
    ) -> Chapter:
        """
        Generate a single chapter for an existing textbook
        """
        # Create the chapter record
        chapter = Chapter(
            title=chapter_title,
            position=position,
            status="GENERATING",
            textbook_id=textbook_id
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

        try:
            # Generate chapter content
            content = await content_generation_service.generate_chapter_content(
                subject="",
                chapter_title=chapter_title,
                educational_level=educational_level,
                include_exercises=include_exercises,
                include_summaries=include_summaries
            )

            # For now, we'll use the content as is, but in a real implementation
            # we would parse it and create sections appropriately
            section = Section(
                title=chapter_title,
                content=content,
                position=1,
                type="CONTENT",
                chapter_id=chapter.id
            )
            db.add(section)

            # Update chapter status to completed
            chapter.status = "COMPLETED"
            db.add(chapter)
            db.commit()

            return chapter

        except Exception as e:
            # If there's an error, mark the chapter as failed
            chapter.status = "FAILED"
            db.add(chapter)
            db.commit()
            raise e

    async def update_content_with_feedback(
        self,
        db: Session,
        content_id: str,
        content_type: str,  # "chapter" or "section"
        feedback: str,
        educational_level: str
    ) -> str:
        """
        Update content based on user feedback
        """
        if content_type == "chapter":
            chapter = db.query(Chapter).filter(Chapter.id == content_id).first()
            if not chapter:
                raise ValueError(f"Chapter with id {content_id} not found")

            # Get all sections in the chapter to form the content
            sections = db.query(Section).filter(Section.chapter_id == content_id).all()
            current_content = "\n\n".join([section.content for section in sections])

            # Improve the content
            improved_content = await content_generation_service.improve_content(
                content=current_content,
                feedback=feedback,
                educational_level=educational_level
            )

            # Update all sections with the improved content
            # In a real implementation, this would involve parsing the improved content
            # and updating sections appropriately
            for section in sections:
                section.content = improved_content
                db.add(section)

            db.commit()
            return improved_content

        elif content_type == "section":
            section = db.query(Section).filter(Section.id == content_id).first()
            if not section:
                raise ValueError(f"Section with id {content_id} not found")

            # Improve the content
            improved_content = await content_generation_service.improve_content(
                content=section.content,
                feedback=feedback,
                educational_level=educational_level
            )

            # Update the section
            section.content = improved_content
            db.add(section)
            db.commit()

            return improved_content

        else:
            raise ValueError(f"Invalid content_type: {content_type}")


# Singleton instance
textbook_generation_service = TextbookGenerationService()