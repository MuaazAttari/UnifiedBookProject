import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.book_service import book_service
from src.models.entities import BookContent
import uuid
import asyncio
import markdown
from bs4 import BeautifulSoup

# DOCS_PATH = Path("../../my-website/docs").resolve()
ROOT = Path(__file__).resolve().parents[2]
DOCS_PATH = ROOT / "my-website" / "docs"
print("DOCS PATH:", DOCS_PATH)
print("EXISTS:", DOCS_PATH.exists())

BOOK_ID = "physical_ai_book"


def md_to_text(md: str) -> str:
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ")


async def ingest():
    contents = []
    idx = 0

    # for md_file in DOCS_PATH.rglob("*.md"):
    for md_file in DOCS_PATH.rglob("*.md*"):

        text = md_to_text(md_file.read_text(encoding="utf-8"))
        if len(text.strip()) < 50:
            continue

        contents.append(
            BookContent(
                book_id=BOOK_ID,
                chapter=md_file.parent.name,
                section=md_file.stem,
                paragraph_index=idx,
                page_number=0,
                content_type="text",
                content=text,
                chunk_id=str(uuid.uuid4())
            )
        )
        idx += 1

    await book_service.index_book_content(contents)
    print(f"Indexed {len(contents)} markdown files into Qdrant")


if __name__ == "__main__":
    asyncio.run(ingest())
