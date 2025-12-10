import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from src.services.rag_service import RAGService, RAGResponse
from src.services.openai_service import ChatResponse
from src.services.embedding_service import SearchResults, DocumentChunk


class TestRAGService:
    """Test suite for RAG service functionality."""

    @pytest.fixture
    def rag_service(self):
        """Create a RAG service instance for testing."""
        with patch('src.services.openai_service.OpenAIService'), \
             patch('src.services.embedding_service.EmbeddingService'):
            service = RAGService()
            service.openai_service = MagicMock()
            service.embedding_service = MagicMock()
            service.logger = MagicMock()
            return service

    @pytest.mark.asyncio
    async def test_process_full_book_query_with_results(self, rag_service):
        """Test processing a full book query with relevant results found."""
        # Mock search results
        mock_chunk = DocumentChunk(
            id="chunk_1",
            content="This is relevant content about the topic",
            metadata={"title": "Chapter 1", "source": "chapter_1.md", "chunk_index": 0}
        )
        mock_search_results = SearchResults(
            chunks=[mock_chunk],
            scores=[8.5]
        )

        # Mock the embedding service search
        rag_service.embedding_service.search = AsyncMock(return_value=mock_search_results)

        # Mock the OpenAI service response
        mock_response = ChatResponse(
            content="This is the answer based on the context.",
            tokens_used=50
        )
        rag_service.openai_service.get_answer_from_context = AsyncMock(return_value=mock_response)

        # Test the method
        result = await rag_service.process_full_book_query(
            query="What is this topic about?",
            max_context_length=2000,
            top_k=5
        )

        # Assertions
        assert isinstance(result, RAGResponse)
        assert result.answer == "This is the answer based on the context."
        assert result.context == "This is relevant content about the topic"
        assert len(result.sources) == 1
        assert result.sources[0]["title"] == "Chapter 1"
        assert result.tokens_used == 50
        assert result.confidence > 0  # Should have some confidence since results were found

    @pytest.mark.asyncio
    async def test_process_full_book_query_no_results(self, rag_service):
        """Test processing a full book query with no relevant results found."""
        # Mock empty search results
        mock_search_results = SearchResults(
            chunks=[],
            scores=[]
        )

        # Mock the embedding service search
        rag_service.embedding_service.search = AsyncMock(return_value=mock_search_results)

        # Mock the OpenAI service response for no context
        mock_response = ChatResponse(
            content="The requested information was not found in the textbook content.",
            tokens_used=30
        )
        rag_service.openai_service.get_completion = AsyncMock(return_value=mock_response)

        # Test the method
        result = await rag_service.process_full_book_query(
            query="What is this topic about?",
            max_context_length=2000,
            top_k=5
        )

        # Assertions
        assert isinstance(result, RAGResponse)
        assert "not found" in result.answer.lower()
        assert result.context == ""
        assert len(result.sources) == 0
        assert result.tokens_used == 30
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_process_selected_text_query(self, rag_service):
        """Test processing a selected text query."""
        # Mock the OpenAI service response
        mock_response = ChatResponse(
            content="This is the answer based on the selected text.",
            tokens_used=45
        )
        rag_service.openai_service.get_answer_from_context = AsyncMock(return_value=mock_response)

        # Test the method
        result = await rag_service.process_selected_text_query(
            query="What does this selected text mean?",
            selected_text="This is the selected text that the user highlighted."
        )

        # Assertions
        assert isinstance(result, RAGResponse)
        assert result.answer == "This is the answer based on the selected text."
        assert result.context == "This is the selected text that the user highlighted."
        assert len(result.sources) == 1
        assert result.sources[0]["title"] == "Selected Text"
        assert result.sources[0]["id"] == "selected_text"
        assert result.tokens_used == 45
        assert result.confidence == 1.0  # High confidence for selected text

    @pytest.mark.asyncio
    async def test_get_relevant_chapters(self, rag_service):
        """Test getting relevant chapters for a query."""
        # Mock search results with multiple chunks from different chapters
        mock_chunks = [
            DocumentChunk(
                id="chunk_1",
                content="Content from chapter 1",
                metadata={"title": "Chapter 1: Introduction", "source": "ch1.md", "chunk_index": 0}
            ),
            DocumentChunk(
                id="chunk_2",
                content="Content from chapter 2",
                metadata={"title": "Chapter 2: Basics", "source": "ch2.md", "chunk_index": 0}
            )
        ]
        mock_search_results = SearchResults(
            chunks=mock_chunks,
            scores=[9.0, 8.5]
        )

        # Mock the embedding service search
        rag_service.embedding_service.search = AsyncMock(return_value=mock_search_results)

        # Test the method
        result = await rag_service.get_relevant_chapters(
            query="Find relevant chapters",
            top_k=2
        )

        # Assertions
        assert isinstance(result, list)
        assert len(result) >= 1  # Should have at least one chapter
        # Note: The actual grouping logic might result in fewer unique chapters than chunks

    @pytest.mark.asyncio
    async def test_answer_with_chapter_context_short_chapter(self, rag_service):
        """Test answering with a short chapter as context."""
        # Mock the OpenAI service response
        mock_response = ChatResponse(
            content="This is the answer based on the chapter.",
            tokens_used=40
        )
        rag_service.openai_service.get_answer_from_context = AsyncMock(return_value=mock_response)

        # Test the method with a short chapter
        result = await rag_service.answer_with_chapter_context(
            query="What does this chapter say?",
            chapter_content="This is a short chapter with basic information.",
            chapter_title="Short Chapter"
        )

        # Assertions
        assert isinstance(result, RAGResponse)
        assert result.answer == "This is the answer based on the chapter."
        assert result.context == "This is a short chapter with basic information."
        assert len(result.sources) == 1
        assert result.sources[0]["title"] == "Short Chapter"
        assert result.tokens_used == 40
        assert result.confidence == 0.9  # High confidence for chapter context

    @pytest.mark.asyncio
    async def test_validate_and_clean_query(self, rag_service):
        """Test query validation and cleaning."""
        # Test normal query
        result = await rag_service.validate_and_clean_query("This is a valid query")
        assert result == "This is a valid query"

        # Test query with excessive whitespace
        result = await rag_service.validate_and_clean_query("   This   has   spaces   ")
        assert result == "This has spaces"

        # Test empty query (should raise ValueError)
        with pytest.raises(ValueError):
            await rag_service.validate_and_clean_query("")

        # Test too long query (should raise ValueError)
        with pytest.raises(ValueError):
            await rag_service.validate_and_clean_query("x" * 1001)

    def test_format_response(self, rag_service):
        """Test response formatting."""
        # Create a test RAG response
        test_response = RAGResponse(
            answer="This is the answer to the question.",
            context="This is the context used to generate the answer.",
            sources=[{
                "id": "source_1",
                "title": "Test Source",
                "source": "test.md",
                "relevance_score": 8.5,
                "content_preview": "This is a preview..."
            }],
            tokens_used=100,
            confidence=0.85
        )

        # Format the response
        formatted = rag_service.format_response(test_response)

        # Assertions
        assert "answer" in formatted
        assert "context" in formatted
        assert "sources" in formatted
        assert "tokens_used" in formatted
        assert "confidence" in formatted
        assert "confidence_percentage" in formatted
        assert formatted["processed"] is True
        assert formatted["confidence_percentage"] == 85.0

    def test_sanitize_response(self, rag_service):
        """Test response sanitization."""
        # Create test response data with potential XSS content
        test_data = {
            "answer": 'This is an answer with <script>alert("xss")</script> content',
            "context": "This is context with <img src=x onerror=alert(1)>",
            "sources": [
                {
                    "title": 'Source with "quotes" and <b>HTML</b>',
                    "content_preview": "<script>malicious</script>"
                }
            ]
        }

        # Sanitize the response
        sanitized = rag_service.sanitize_response(test_data)

        # Assertions - HTML should be escaped
        assert "<script>" not in sanitized["answer"]
        assert "&lt;script&gt;" in sanitized["answer"]
        assert "<img" not in sanitized["context"]
        assert "&lt;img" in sanitized["context"]
        assert "<b>" not in sanitized["sources"][0]["title"]
        assert "&lt;b&gt;" in sanitized["sources"][0]["title"]
        assert "<script>" not in sanitized["sources"][0]["content_preview"]
        assert "&lt;script&gt;" in sanitized["sources"][0]["content_preview"]


class TestRAGIntegration:
    """Integration tests for RAG functionality."""

    @pytest.mark.asyncio
    async def test_full_rag_flow(self):
        """Test the complete RAG flow from query to response."""
        # This would require actual OpenAI and embedding services
        # For now, we'll just verify the structure works
        rag_service = RAGService()

        # We can't run full integration without actual API keys,
        # but we can verify the service is properly initialized
        assert hasattr(rag_service, 'openai_service')
        assert hasattr(rag_service, 'embedding_service')
        assert hasattr(rag_service, 'logger')