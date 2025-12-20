"""
Markdown Ingestion Script for Physical AI Book

This script processes markdown files from the Docusaurus docs directory,
converts them to plain text, chunks them appropriately, embeds them using
Cohere, and stores the vectors in Qdrant.
"""
import asyncio
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.ingestion_service import index_physical_ai_book


async def main():
    """
    Main entry point for the script
    """
    # Default book ID, but could accept as command line argument
    book_id = "physical-ai-book"

    if len(sys.argv) > 1:
        book_id = sys.argv[1]

    try:
        await index_physical_ai_book(book_id)
    except Exception as e:
        print(f"Error during ingestion: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())