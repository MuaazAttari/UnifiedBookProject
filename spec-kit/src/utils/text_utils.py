def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """
    Split text into chunks of specified size with overlap.

    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If this is the last chunk, include the rest
        if end >= len(text):
            chunks.append(text[start:])
            break

        # Try to break at sentence or word boundary
        chunk = text[start:end]

        # Find the last sentence or word boundary before the chunk limit
        if end < len(text):
            # Look for sentence boundaries first
            sentence_break = chunk.rfind('. ')
            if sentence_break == -1:
                # Look for word boundary
                sentence_break = chunk.rfind(' ')

            if sentence_break != -1 and sentence_break > chunk_size // 2:
                # Break at the boundary and include overlap
                actual_end = start + sentence_break + 1
                chunks.append(text[start:actual_end])
                start = actual_end - overlap if overlap < actual_end - start else actual_end
            else:
                # No good break point found, just take the chunk
                chunks.append(text[start:end])
                start = end - overlap
        else:
            chunks.append(text[start:end])
            break

    return chunks


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    cleaned = ' '.join(text.split())
    return cleaned


def extract_sentences(text: str) -> list[str]:
    """
    Extract sentences from text.

    Args:
        text: Text to extract sentences from

    Returns:
        List of sentences
    """
    import re
    # Split text by sentence endings
    sentences = re.split(r'[.!?]+', text)
    # Remove empty strings and strip whitespace
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences