"""
Markdown Ingestion Service

This module contains the core logic for processing markdown files from the Docusaurus docs directory,
converting them to plain text, chunking them appropriately, embedding them using
Cohere, and storing the vectors in Qdrant.
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import List
import uuid

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.entities import BookContent, BookContentType
from src.services.book_service import book_service
from src.utils.markdown_parser import clean_markdown_to_text, extract_chapter_section_info, chunk_markdown_content


async def process_markdown_files(book_id: str, source_dir: str) -> List[BookContent]:
    """
    Process all markdown files in the specified directory
    """
    source_path = Path(source_dir)
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    
    # Get all markdown files
    md_files = list(source_path.glob('**/*.md'))
    print(f"Found {len(md_files)} markdown files to process")
    
    all_book_contents = []
    
    for i, md_file in enumerate(md_files):
        print(f"Processing file {i+1}/{len(md_files)}: {md_file.name}")
        
        # Read the markdown file content
        with open(md_file, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        # Clean markdown to plain text
        plain_text = clean_markdown_to_text(markdown_content)
        
        # Extract chapter/section info
        chapter_title, section_title = extract_chapter_section_info(str(md_file), markdown_content)
        
        # Chunk the content
        chunks = chunk_markdown_content(plain_text, max_chunk_size=500, overlap=50)
        
        # Create BookContent entities for each chunk
        for j, chunk in enumerate(chunks):
            book_content = BookContent(
                book_id=book_id,
                chapter=chapter_title,
                section=section_title,
                paragraph_index=j,
                page_number=0,  # Not applicable for markdown docs, using 0 as default
                content_type=BookContentType.TEXT,
                content=chunk,
                chunk_id=str(uuid.uuid4())  # Use UUID string as ID
            )
            all_book_contents.append(book_content)
    
    print(f"Total chunks created: {len(all_book_contents)}")
    return all_book_contents


async def index_physical_ai_book(book_id: str = "physical-ai-book"):
    """
    Main function to index the Physical AI book from markdown files
    """
    print(f"Starting ingestion for book: {book_id}")

    # Define the source directory by building the path from the service file location
    # The service file is in: backend/src/services/ingestion_service.py
    # So we need to go up 4 levels to get to the project root (Physical_AI_Book)
    service_file_path = Path(__file__).resolve()
    src_path = service_file_path.parent.parent  # Go up 2 levels to src
    backend_path = src_path.parent  # Go up 1 level to backend
    project_root = backend_path.parent  # Go up 1 level to project root (Physical_AI_Book)
    source_dir = project_root / "my-website" / "docs" / "physical-ai"

    if not source_dir.exists():
        print(f"Error: Source directory does not exist: {source_dir}")
        print("Make sure you're running this script from the backend directory.")
        return
    
    # Process markdown files
    book_contents = await process_markdown_files(book_id, str(source_dir))
    
    if not book_contents:
        print("No content to index. Exiting.")
        return
    
    # Index the content
    print("Indexing content into vector database...")
    await book_service.index_book_content(book_contents)
    
    print(f"Indexing completed successfully! Indexed {len(book_contents)} content chunks.")
    return book_contents