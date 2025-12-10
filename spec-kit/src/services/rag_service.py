import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.services.openai_service import OpenAIService, ChatResponse
from src.services.embedding_service import EmbeddingService, SearchResults
from src.services.chapter_service import ChapterService
from src.models.chat_session import ChatSession
from src.db.database import get_db
from src.utils.response_formatter import ResponseFormatter


@dataclass
class RAGResponse:
    """Data class to represent a RAG response."""
    answer: str
    context: str
    sources: List[Dict[str, Any]]
    tokens_used: int
    confidence: float


class RAGService:
    """Service class for RAG (Retrieval-Augmented Generation) functionality."""

    def __init__(self):
        self.openai_service = OpenAIService()
        self.embedding_service = EmbeddingService()
        self.logger = logging.getLogger(__name__)

    async def process_full_book_query(
        self,
        query: str,
        user_id: Optional[str] = None,
        max_context_length: int = 2000,
        top_k: int = 5
    ) -> RAGResponse:
        """
        Process a query against the full book content using RAG.

        Args:
            query: User's question
            user_id: Optional user ID for tracking
            max_context_length: Maximum length of context to include
            top_k: Number of top results to retrieve

        Returns:
            RAGResponse object with answer, context, and sources
        """
        try:
            # Search for relevant chunks in the vector store
            search_results = await self.embedding_service.search(
                query=query,
                collection_name="textbook_content",
                top_k=top_k
            )

            if not search_results.chunks:
                # No relevant content found
                answer_response = await self.openai_service.get_completion(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. The requested information was not found in the textbook content."},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.3
                )

                return RAGResponse(
                    answer=answer_response.content,
                    context="",
                    sources=[],
                    tokens_used=answer_response.tokens_used,
                    confidence=0.0
                )

            # Combine the most relevant chunks to form context
            context_parts = []
            total_length = 0

            for chunk in search_results.chunks:
                chunk_text = chunk.content.strip()
                if total_length + len(chunk_text) <= max_context_length:
                    context_parts.append(chunk_text)
                    total_length += len(chunk_text)
                else:
                    # Add partial chunk if there's remaining space
                    remaining_space = max_context_length - total_length
                    if remaining_space > 0:
                        partial_chunk = chunk_text[:remaining_space]
                        context_parts.append(partial_chunk)
                    break

            context = "\n\n".join(context_parts)

            # Generate answer using the context
            answer_response = await self.openai_service.get_answer_from_context(
                query=query,
                context=context
            )

            # Prepare sources information
            sources = []
            for chunk, score in zip(search_results.chunks, search_results.scores):
                sources.append({
                    "id": chunk.id,
                    "title": chunk.metadata.get("title", ""),
                    "source": chunk.metadata.get("source", ""),
                    "chunk_index": chunk.metadata.get("chunk_index", 0),
                    "relevance_score": score,
                    "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
                })

            # Calculate confidence based on relevance scores
            avg_score = sum(search_results.scores) / len(search_results.scores) if search_results.scores else 0
            confidence = min(avg_score / 10.0, 1.0)  # Normalize to 0-1 range

            return RAGResponse(
                answer=answer_response.content,
                context=context,
                sources=sources,
                tokens_used=answer_response.tokens_used,
                confidence=confidence
            )

        except Exception as e:
            self.logger.error(f"Error processing full book query: {str(e)}")
            raise

    async def process_selected_text_query(
        self,
        query: str,
        selected_text: str,
        user_id: Optional[str] = None
    ) -> RAGResponse:
        """
        Process a query against selected text using RAG.

        Args:
            query: User's question
            selected_text: Text that was selected/highlighted by user
            user_id: Optional user ID for tracking

        Returns:
            RAGResponse object with answer and context
        """
        try:
            # Use the selected text as context
            context = selected_text

            # Generate answer using the selected text as context
            answer_response = await self.openai_service.get_answer_from_context(
                query=query,
                context=context
            )

            # For selected text queries, we use the selected text as the source
            sources = [{
                "id": "selected_text",
                "title": "Selected Text",
                "source": "user_selection",
                "relevance_score": 1.0,
                "content_preview": selected_text[:200] + "..." if len(selected_text) > 200 else selected_text
            }]

            return RAGResponse(
                answer=answer_response.content,
                context=context,
                sources=sources,
                tokens_used=answer_response.tokens_used,
                confidence=1.0  # High confidence since we're using exact selected text
            )

        except Exception as e:
            self.logger.error(f"Error processing selected text query: {str(e)}")
            raise

    async def get_relevant_chapters(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find the most relevant chapters for a given query.

        Args:
            query: Search query
            top_k: Number of top chapters to return

        Returns:
            List of relevant chapters with metadata
        """
        try:
            # Search for relevant chunks
            search_results = await self.embedding_service.search(
                query=query,
                collection_name="textbook_content",
                top_k=top_k * 3  # Get more chunks to identify unique chapters
            )

            # Group chunks by chapter/source
            chapter_map = {}
            for chunk in search_results.chunks:
                source = chunk.metadata.get("source", "unknown")
                if source not in chapter_map:
                    chapter_map[source] = {
                        "source": source,
                        "title": chunk.metadata.get("title", source),
                        "chunks": [],
                        "total_score": 0
                    }
                chapter_map[source]["chunks"].append(chunk)
                # Add the score of the best chunk as the chapter score
                chapter_map[source]["total_score"] += max(
                    chunk.metadata.get("chunk_index", 0),  # Using index as proxy for score
                    chunk.metadata.get("relevance_score", 0)
                )

            # Sort chapters by total score and return top_k
            sorted_chapters = sorted(
                chapter_map.values(),
                key=lambda x: x["total_score"],
                reverse=True
            )[:top_k]

            return sorted_chapters

        except Exception as e:
            self.logger.error(f"Error finding relevant chapters: {str(e)}")
            return []

    async def answer_with_chapter_context(
        self,
        query: str,
        chapter_content: str,
        chapter_title: str = ""
    ) -> RAGResponse:
        """
        Answer a query using a specific chapter as context.

        Args:
            query: User's question
            chapter_content: Content of the chapter to use as context
            chapter_title: Title of the chapter

        Returns:
            RAGResponse object with answer and context
        """
        try:
            # Split chapter into chunks if it's very long
            if len(chapter_content) > 3000:  # If chapter is longer than ~3000 chars
                chunks = self.embedding_service.chunk_text(
                    chapter_content,
                    chunk_size=1000,
                    overlap=100
                )
                # Combine relevant chunks based on query
                context = self._select_relevant_chunks_for_query(chunks, query)
            else:
                context = chapter_content

            # Generate answer using the chapter context
            answer_response = await self.openai_service.get_answer_from_context(
                query=query,
                context=context
            )

            # Prepare sources information
            sources = [{
                "id": "chapter_context",
                "title": chapter_title,
                "source": "chapter",
                "relevance_score": 1.0,
                "content_preview": context[:200] + "..." if len(context) > 200 else context
            }]

            return RAGResponse(
                answer=answer_response.content,
                context=context,
                sources=sources,
                tokens_used=answer_response.tokens_used,
                confidence=0.9  # High confidence when using full chapter context
            )

        except Exception as e:
            self.logger.error(f"Error answering with chapter context: {str(e)}")
            raise

    def _select_relevant_chunks_for_query(
        self,
        chunks: List,
        query: str
    ) -> str:
        """
        Select the most relevant chunks for a query (simplified approach).

        Args:
            chunks: List of text chunks
            query: Query to match against

        Returns:
            Combined relevant content
        """
        # Simple approach: return chunks that contain query keywords
        query_lower = query.lower()
        relevant_parts = []

        for chunk in chunks:
            chunk_content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            if any(keyword in chunk_content.lower() for keyword in query_lower.split()[:3]):  # Use first 3 words as keywords
                relevant_parts.append(chunk_content)

        # Limit total length
        total_content = ""
        for part in relevant_parts:
            if len(total_content) + len(part) < 2000:  # Limit to 2000 chars
                total_content += part + "\n\n"
            else:
                break

        return total_content.strip()

    async def validate_and_clean_query(self, query: str) -> str:
        """
        Validate and clean the user query.

        Args:
            query: Raw user query

        Returns:
            Cleaned and validated query
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Remove excessive whitespace
        cleaned_query = " ".join(query.split())

        # Basic length validation
        if len(cleaned_query) > 1000:
            raise ValueError("Query is too long (max 1000 characters)")

        return cleaned_query

    async def generate_query_embeddings(self, query: str) -> List[float]:
        """
        Generate embeddings for a query.

        Args:
            query: Query string

        Returns:
            Embedding vector
        """
        embeddings = await self.openai_service.generate_embeddings([query])
        return embeddings[0]  # Return the first (and only) embedding

    def format_response(self, response: RAGResponse, add_citations: bool = True) -> Dict[str, Any]:
        """
        Format a RAG response for display.

        Args:
            response: RAGResponse object to format
            add_citations: Whether to add citations to the answer

        Returns:
            Formatted response dictionary
        """
        return ResponseFormatter.post_process_response(response, add_citations)

    def sanitize_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize response content to prevent XSS or other injection issues.

        Args:
            response_data: Response data dictionary

        Returns:
            Sanitized response data
        """
        return ResponseFormatter.sanitize_response_content(response_data)


# Global instance
rag_service = RAGService()