import uuid
import json
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.chapter import Chapter


class ChapterService:
    @staticmethod
    def get_chapter(db: Session, chapter_id: str) -> Optional[Chapter]:
        """
        Retrieve a chapter by ID.
        """
        return db.query(Chapter).filter(Chapter.chapter_id == chapter_id).first()

    @staticmethod
    def get_chapter_by_slug(db: Session, slug: str) -> Optional[Chapter]:
        """
        Retrieve a chapter by slug.
        """
        return db.query(Chapter).filter(Chapter.slug == slug).first()

    @staticmethod
    def get_chapters_by_order(db: Session, skip: int = 0, limit: int = 100) -> List[Chapter]:
        """
        Retrieve chapters ordered by sequence.
        """
        return db.query(Chapter).order_by(Chapter.order).offset(skip).limit(limit).all()

    @staticmethod
    def get_chapters_by_path(db: Session, path: str) -> List[Chapter]:
        """
        Retrieve chapters by path.
        """
        return db.query(Chapter).filter(Chapter.path.like(f"%{path}%")).all()

    @staticmethod
    def create_chapter(
        db: Session,
        title: str,
        content: str,
        frontmatter: dict,
        order: int,
        path: str,
        slug: str,
        description: Optional[str] = None
    ) -> Chapter:
        """
        Create a new chapter.
        """
        chapter_id = str(uuid.uuid4())
        frontmatter_str = json.dumps(frontmatter) if isinstance(frontmatter, dict) else frontmatter

        db_chapter = Chapter(
            chapter_id=chapter_id,
            title=title,
            content=content,
            frontmatter=frontmatter_str,
            order=order,
            path=path,
            slug=slug,
            description=description
        )
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        return db_chapter

    @staticmethod
    def update_chapter(
        db: Session,
        chapter_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        frontmatter: Optional[dict] = None,
        order: Optional[int] = None,
        path: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Chapter]:
        """
        Update an existing chapter.
        """
        db_chapter = db.query(Chapter).filter(Chapter.chapter_id == chapter_id).first()
        if db_chapter:
            if title is not None:
                db_chapter.title = title
            if content is not None:
                db_chapter.content = content
            if frontmatter is not None:
                db_chapter.frontmatter = json.dumps(frontmatter)
            if order is not None:
                db_chapter.order = order
            if path is not None:
                db_chapter.path = path
            if slug is not None:
                db_chapter.slug = slug
            if description is not None:
                db_chapter.description = description

            db.commit()
            db.refresh(db_chapter)
        return db_chapter

    @staticmethod
    def delete_chapter(db: Session, chapter_id: str) -> bool:
        """
        Delete a chapter.
        """
        db_chapter = db.query(Chapter).filter(Chapter.chapter_id == chapter_id).first()
        if db_chapter:
            db.delete(db_chapter)
            db.commit()
            return True
        return False

    @staticmethod
    def get_chapters_by_docs_folder(db: Session, docs_folder: str) -> List[Chapter]:
        """
        Retrieve all chapters for a specific docs folder.
        """
        return db.query(Chapter).filter(Chapter.path.like(f"{docs_folder}%")).all()