"""
Utility functions for parsing markdown content and converting to plain text
"""
import re
from typing import List, Tuple
import frontmatter  # For parsing markdown frontmatter


def clean_markdown_to_text(markdown_content: str) -> str:
    """
    Convert markdown content to plain text by removing markdown syntax
    while preserving the content.
    """
    # Remove frontmatter (content between --- delimiters)
    content = re.sub(r'^---\n.*?\n---\n', '', markdown_content, flags=re.DOTALL)

    # Remove markdown headers (# Header)
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

    # Remove emphasis markers (*italic*, **bold**, _italic_, __bold__)
    content = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', content)
    content = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', content)

    # Remove inline code markers (`code`)
    content = re.sub(r'`(.*?)`', r'\1', content)

    # Remove links [text](url) and images ![alt](url)
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)

    # Remove image references
    content = re.sub(r'!\[.*?\]\[.*?\]', '', content)

    # Remove horizontal rules
    content = re.sub(r'^\s*[-*_]{3,}\s*$', '', content, flags=re.MULTILINE)

    # Remove list markers
    content = re.sub(r'^\s*[*+-]\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)

    # Remove blockquotes
    content = re.sub(r'^\s*>\s*', '', content, flags=re.MULTILINE)

    # Remove extra whitespace and normalize spacing
    content = re.sub(r'\n\s*\n', '\n\n', content)  # Multiple newlines to double newline
    content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single space
    content = content.strip()

    return content


def extract_chapter_section_info(file_path: str, content: str) -> Tuple[str, str]:
    """
    Extract chapter and section information from file path and content.
    """
    # Get filename without extension to use as identifier
    import os
    filename = os.path.splitext(os.path.basename(file_path))[0]

    # Try to extract title from frontmatter
    try:
        post = frontmatter.loads(content)
        title = post.get('title', '').strip()
        if title:
            return title, post.get('sidebar_label', title)
    except:
        pass  # If no frontmatter, fall back to filename

    # If no title in frontmatter, use the filename
    return filename, filename.replace('-', ' ').title()


def chunk_markdown_content(content: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Chunk markdown content into smaller pieces, trying to preserve sentence boundaries.
    """
    # Split content into paragraphs first
    paragraphs = content.split('\n\n')

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # If adding this paragraph would exceed the chunk size
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            # Add the current chunk to the list
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            # Start a new chunk with this paragraph
            current_chunk = paragraph
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

        # If current chunk is getting too large, split it by sentences
        if len(current_chunk) > max_chunk_size:
            sentences = re.split(r'([.!?]+\s+)', current_chunk)
            temp_chunk = ""

            for sentence in sentences:
                if len(temp_chunk) + len(sentence) <= max_chunk_size:
                    temp_chunk += sentence
                else:
                    if temp_chunk.strip():
                        chunks.append(temp_chunk.strip())
                    temp_chunk = sentence

            current_chunk = temp_chunk

    # Add the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Filter out very small chunks unless it's the only one
    if len(chunks) > 1:
        chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]

    # Add overlap between chunks if needed
    if overlap > 0 and len(chunks) > 1:
        overlapping_chunks = []
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:  # Last chunk
                overlapping_chunks.append(chunk)
            else:
                # Add overlap from the next chunk
                next_chunk_start = chunks[i + 1][:overlap]
                if next_chunk_start.strip():
                    chunk_with_overlap = chunk + " " + next_chunk_start.strip()
                    overlapping_chunks.append(chunk_with_overlap)
                else:
                    overlapping_chunks.append(chunk)
        chunks = overlapping_chunks

    return chunks