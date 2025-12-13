"""
Script to reindex all documentation into the RAG system
"""
import asyncio
import os
import glob
from pathlib import Path
import re
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from src.rag_chat.rag_service import RAGService
from src.database.session import SessionLocal
from src.config.settings import settings


def extract_frontmatter(content: str) -> Dict[str, Any]:
    """
    Extract frontmatter from markdown content
    """
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        # Simple parsing of YAML-like frontmatter
        result = {}
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip().strip('"\'')
        return result
    return {}


def chunk_text(text: str, chunk_size: int = 512) -> List[str]:
    """
    Split text into chunks of specified size
    """
    sentences = re.split(r'[.!?]+\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def read_markdown_files(docs_path: str) -> List[Dict[str, Any]]:
    """
    Read all markdown files from the docs directory
    """
    files = glob.glob(os.path.join(docs_path, "**/*.md"), recursive=True)
    documents = []

    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter
        frontmatter = extract_frontmatter(content)

        # Get content without frontmatter
        content_without_frontmatter = re.sub(r'^---\n(.*?)\n---\n?', '', content, flags=re.DOTALL)

        # Create document object
        doc = {
            "doc_id": Path(file_path).stem,
            "title": frontmatter.get("title", Path(file_path).stem),
            "content": content_without_frontmatter,
            "path": file_path,
            "frontmatter": frontmatter
        }
        documents.append(doc)

    return documents


async def reindex_all_documents():
    """
    Main function to reindex all documentation
    """
    print("Starting reindexing process...")

    # Initialize RAG service
    rag_service = RAGService()
    rag_service.initialize()

    # Get database session
    db: Session = SessionLocal()

    try:
        # Path to documentation
        docs_path = os.path.join(settings.base_dir, "..", "..", "my-website", "docs")
        docs_path = os.path.abspath(docs_path)

        print(f"Reading documentation from: {docs_path}")

        # Read all markdown files
        documents = read_markdown_files(docs_path)

        print(f"Found {len(documents)} documents to process")

        # Process each document
        for i, doc in enumerate(documents):
            print(f"Processing document {i+1}/{len(documents)}: {doc['title']}")

            # Chunk the content
            text_chunks = chunk_text(doc['content'])

            # Prepare metadata for each chunk
            metadata_list = []
            for j, chunk in enumerate(text_chunks):
                meta = {
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "path": doc["path"],
                    "chunk_index": j,
                    "total_chunks": len(text_chunks),
                    **doc["frontmatter"]  # Include frontmatter fields
                }
                metadata_list.append(meta)

            # Ingest into RAG service
            await rag_service.ingest_document(
                doc_id=doc["doc_id"],
                text_chunks=text_chunks,
                metadata=metadata_list
            )

        print(f"Successfully reindexed {len(documents)} documents")

    except Exception as e:
        print(f"Error during reindexing: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(reindex_all_documents())