from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas import ChapterCreate, ChapterUpdate, Chapter as ChapterSchema
from src.services.chapter_service import ChapterService

router = APIRouter()


@router.post("/", response_model=ChapterSchema)
def create_chapter(
    chapter: ChapterCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new chapter.
    """
    # Check if chapter with this slug already exists
    db_chapter = ChapterService.get_chapter_by_slug(db, chapter.slug)
    if db_chapter:
        raise HTTPException(
            status_code=400,
            detail="Chapter with this slug already exists"
        )

    return ChapterService.create_chapter(
        db=db,
        title=chapter.title,
        content=chapter.content,
        frontmatter=chapter.frontmatter,
        order=chapter.order,
        path=chapter.path,
        slug=chapter.slug,
        description=chapter.description
    )


@router.get("/", response_model=list[ChapterSchema])
def read_chapters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve chapters with optional pagination.
    """
    chapters = ChapterService.get_chapters_by_order(db, skip=skip, limit=limit)
    return chapters


@router.get("/{chapter_id}", response_model=ChapterSchema)
def read_chapter(chapter_id: str, db: Session = Depends(get_db)):
    """
    Get chapter by ID.
    """
    chapter = ChapterService.get_chapter(db, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/{chapter_id}", response_model=ChapterSchema)
def update_chapter(
    chapter_id: str,
    chapter_update: ChapterUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing chapter.
    """
    updated_chapter = ChapterService.update_chapter(
        db=db,
        chapter_id=chapter_id,
        title=chapter_update.title,
        content=chapter_update.content,
        frontmatter=chapter_update.frontmatter,
        order=chapter_update.order,
        path=chapter_update.path,
        slug=chapter_update.slug,
        description=chapter_update.description
    )
    if updated_chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return updated_chapter


@router.delete("/{chapter_id}")
def delete_chapter(chapter_id: str, db: Session = Depends(get_db)):
    """
    Delete a chapter.
    """
    deleted = ChapterService.delete_chapter(db, chapter_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"message": "Chapter deleted successfully"}


@router.get("/by-path/{path:path}", response_model=list[ChapterSchema])
def read_chapters_by_path(path: str, db: Session = Depends(get_db)):
    """
    Get chapters by path.
    """
    chapters = ChapterService.get_chapters_by_path(db, path)
    return chapters


@router.get("/by-slug/{slug}", response_model=ChapterSchema)
def read_chapter_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Get chapter by slug.
    """
    chapter = ChapterService.get_chapter_by_slug(db, slug)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter