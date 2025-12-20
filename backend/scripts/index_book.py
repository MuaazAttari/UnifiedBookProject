"""
Book Ingestion Script

This script processes book content, chunks it, generates embeddings, 
and indexes it into the Qdrant vector database.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.entities import BookContent
from src.services.book_service import book_service
from src.config.settings import settings


async def load_book_content_from_file(file_path: str, book_id: str) -> List[BookContent]:
    """
    Load book content from a file and convert to BookContent entities
    This is a basic implementation - in practice, you might want to support
    different formats like PDF, EPUB, etc.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # For this example, we'll do a simple chunking strategy
    # In a real implementation, you'd want more sophisticated chunking
    # that respects chapter/section boundaries
    chunks = chunk_book_content(content, chunk_size=500)  # 500 characters per chunk
    
    book_contents = []
    for i, chunk in enumerate(chunks):
        book_content = BookContent(
            book_id=book_id,
            chapter=f"Section_{i // 10 + 1}",  # Group every 10 chunks into a section
            section=f"Part_{i + 1}",
            paragraph_index=i,
            page_number=None,  # Would need to extract from source if available
            content_type="text",
            content=chunk,
            chunk_id=f"{book_id}_chunk_{i}"
        )
        book_contents.append(book_content)
    
    return book_contents


def chunk_book_content(content: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Simple chunking strategy with overlap to maintain context
    """
    chunks = []
    start = 0
    
    while start < len(content):
        end = start + chunk_size
        
        # Try to break at sentence boundary if possible
        if end < len(content):
            # Look for sentence endings near the end
            search_start = max(start, end - 100)  # Look for punctuation in the last 100 chars
            for i in range(end, search_start, -1):
                if content[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = content[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move start position
        start = end - overlap if end < len(content) else end
    
    # Remove any chunks that are too short (unless it's the only chunk)
    if len(chunks) > 1:
        chunks = [chunk for chunk in chunks if len(chunk) > 50]
    
    return chunks


async def index_book(book_id: str, file_path: str):
    """
    Main function to load a book and index it
    """
    print(f"Loading book {book_id} from {file_path}...")
    
    # Load book content from file
    book_contents = await load_book_content_from_file(file_path, book_id)
    
    print(f"Loaded {len(book_contents)} content chunks")
    
    # Index the content
    print("Indexing content into vector database...")
    await book_service.index_book_content(book_contents)
    
    print("Indexing completed successfully!")


async def main():
    """
    Main entry point for the script
    """
    if len(sys.argv) < 3:
        print("Usage: python index_book.py <book_id> <file_path>")
        sys.exit(1)
    
    book_id = sys.argv[1]
    file_path = sys.argv[2]
    
    # Validate inputs
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)
    
    try:
        await index_book(book_id, file_path)
    except Exception as e:
        print(f"Error indexing book: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())