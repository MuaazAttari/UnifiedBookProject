import pytest
from src.utils.response_formatter import ResponseFormatter
from src.services.rag_service import RAGResponse


class TestResponseFormatter:
    """Test suite for the ResponseFormatter utility."""

    def test_format_answer_basic(self):
        """Test basic answer formatting."""
        original = "this is a basic answer"
        formatted = ResponseFormatter.format_answer(original)
        assert formatted == "This is a basic answer."  # Capitalized and punctuated

    def test_format_answer_with_punctuation(self):
        """Test answer formatting with existing punctuation."""
        original = "This is an answer with punctuation!"
        formatted = ResponseFormatter.format_answer(original)
        assert formatted == "This is an answer with punctuation!"

    def test_format_answer_excessive_whitespace(self):
        """Test formatting of answers with excessive whitespace."""
        original = "   this   has   excessive   spaces   "
        formatted = ResponseFormatter.format_answer(original)
        assert formatted == "This has excessive spaces."

    def test_format_answer_remove_prefixes(self):
        """Test removal of common answer prefixes."""
        prefixes = ["Answer: This is the answer", "Response: This is the response", "Question: This is the question"]
        expected = ["This is the answer.", "This is the response.", "This is the question."]

        for i, prefix in enumerate(prefixes):
            formatted = ResponseFormatter.format_answer(prefix)
            assert formatted == expected[i]

    def test_format_answer_empty(self):
        """Test formatting of empty answers."""
        assert ResponseFormatter.format_answer("") == ""
        assert ResponseFormatter.format_answer("   ") == " "

    def test_format_sources_basic(self):
        """Test basic source formatting."""
        sources = [{
            "id": "source_1",
            "title": "Test Chapter",
            "source": "test.md",
            "relevance_score": 8.5,
            "content_preview": "This is a preview...",
            "chunk_index": 1
        }]

        formatted = ResponseFormatter.format_sources(sources)
        assert len(formatted) == 1
        assert formatted[0]["id"] == "source_1"
        assert formatted[0]["title"] == "Test Chapter"
        assert formatted[0]["source"] == "test.md"
        assert formatted[0]["relevance_score"] == 8.5
        assert formatted[0]["content_preview"] == "This is a preview..."
        assert formatted[0]["chunk_index"] == 1

    def test_format_sources_missing_fields(self):
        """Test source formatting with missing fields."""
        sources = [{
            "id": "source_1",
            # Missing other fields
        }]

        formatted = ResponseFormatter.format_sources(sources)
        assert len(formatted) == 1
        assert formatted[0]["id"] == "source_1"
        assert formatted[0]["title"] == ""
        assert formatted[0]["source"] == ""
        assert formatted[0]["relevance_score"] == 0.0
        assert formatted[0]["content_preview"] == ""
        assert formatted[0]["chunk_index"] == 0

    def test_format_sources_empty(self):
        """Test formatting of empty sources list."""
        formatted = ResponseFormatter.format_sources([])
        assert formatted == []

    def test_format_response_for_display(self):
        """Test formatting of complete RAG response."""
        rag_response = RAGResponse(
            answer="This is the answer to the question.",
            context="This is the context used for the answer.",
            sources=[{
                "id": "source_1",
                "title": "Test Chapter",
                "source": "test.md",
                "relevance_score": 8.5,
                "content_preview": "This is a preview...",
                "chunk_index": 1
            }],
            tokens_used=100,
            confidence=0.85
        )

        formatted = ResponseFormatter.format_response_for_display(rag_response)

        assert "answer" in formatted
        assert "context" in formatted
        assert "sources" in formatted
        assert "tokens_used" in formatted
        assert "confidence" in formatted
        assert "formatted" in formatted

        assert formatted["answer"] == "This is the answer to the question."
        assert formatted["context"] == "This is the context used for the answer."
        assert formatted["tokens_used"] == 100
        assert formatted["confidence"] == 0.85
        assert formatted["formatted"] is True
        assert len(formatted["sources"]) == 1

    def test_add_citations_to_answer(self):
        """Test adding citations to answers."""
        answer = "This is the answer based on the information."
        sources = [
            {"title": "Source One"},
            {"title": "Source Two"}
        ]

        result = ResponseFormatter.add_citations_to_answer(answer, sources)

        assert "This is the answer based on the information." in result
        assert "Based on information from 2 sources:" in result
        assert "[1] Source One" in result
        assert "[2] Source Two" in result

    def test_add_citations_to_answer_single_source(self):
        """Test adding citations for single source."""
        answer = "This is the answer."
        sources = [{"title": "Single Source"}]

        result = ResponseFormatter.add_citations_to_answer(answer, sources)

        assert "Based on information from 1 source:" in result

    def test_add_citations_to_answer_no_sources(self):
        """Test adding citations when there are no sources."""
        answer = "This is the answer."
        sources = []

        result = ResponseFormatter.add_citations_to_answer(answer, sources)

        assert result == "This is the answer."

    def test_post_process_response(self):
        """Test complete post-processing of response."""
        rag_response = RAGResponse(
            answer="this is the raw answer",
            context="This is the context.",
            sources=[{
                "id": "source_1",
                "title": "Test Chapter",
                "source": "test.md",
                "relevance_score": 8.5,
                "content_preview": "This is a preview...",
                "chunk_index": 1
            }],
            tokens_used=100,
            confidence=0.857
        )

        processed = ResponseFormatter.post_process_response(rag_response)

        assert processed["answer"] == "This is the raw answer."  # Formatted and citations added
        assert processed["context"] == "This is the context."
        assert processed["tokens_used"] == 100
        assert processed["confidence"] == 0.857  # Rounded to 3 decimal places
        assert processed["confidence_percentage"] == 85.7  # Converted to percentage
        assert processed["processed"] is True

    def test_post_process_response_without_citations(self):
        """Test post-processing without adding citations."""
        rag_response = RAGResponse(
            answer="this is the raw answer",
            context="This is the context.",
            sources=[{
                "id": "source_1",
                "title": "Test Chapter",
                "source": "test.md",
                "relevance_score": 8.5,
                "content_preview": "This is a preview...",
                "chunk_index": 1
            }],
            tokens_used=100,
            confidence=0.85
        )

        processed = ResponseFormatter.post_process_response(rag_response, add_citations=False)

        # The answer should be formatted but without citations
        assert "Based on information from" not in processed["answer"]
        assert processed["processed"] is True

    def test_sanitize_response_content(self):
        """Test sanitization of response content."""
        response_data = {
            "answer": 'This answer has <script>alert("xss")</script> content',
            "context": 'Context with <img src="x" onerror="alert(1)">',
            "sources": [
                {
                    "title": 'Source with "quotes" and <b>HTML</b>',
                    "content_preview": "<script>malicious</script>"
                }
            ]
        }

        sanitized = ResponseFormatter.sanitize_response_content(response_data)

        # Check that HTML tags are escaped
        assert "<script>" not in sanitized["answer"]
        assert "&lt;script&gt;" in sanitized["answer"]
        assert "<img" not in sanitized["context"]
        assert "&lt;img" in sanitized["context"]
        assert "<b>" not in sanitized["sources"][0]["title"]
        assert "&lt;b&gt;" in sanitized["sources"][0]["title"]
        assert "<script>" not in sanitized["sources"][0]["content_preview"]
        assert "&lt;script&gt;" in sanitized["sources"][0]["content_preview"]

    def test_sanitize_response_content_preserves_normal_content(self):
        """Test that normal content is preserved during sanitization."""
        response_data = {
            "answer": "This is a normal answer with quotes \"and\" punctuation.",
            "context": "Normal context with legitimate content.",
            "sources": [
                {
                    "title": "Normal Source Title",
                    "content_preview": "Normal preview content."
                }
            ]
        }

        sanitized = ResponseFormatter.sanitize_response_content(response_data)

        # Normal content should be preserved
        assert "quotes" in sanitized["answer"]
        assert "and" in sanitized["answer"]
        assert "Normal context" in sanitized["context"]
        assert "Normal Source Title" in sanitized["sources"][0]["title"]

    def test_sanitize_response_content_empty_values(self):
        """Test sanitization with empty or None values."""
        response_data = {
            "answer": "",
            "context": None,
            "sources": []
        }

        # This should not raise an exception
        sanitized = ResponseFormatter.sanitize_response_content(response_data)

        assert sanitized["answer"] == ""
        assert sanitized["context"] is None
        assert sanitized["sources"] == []


class TestResponseFormatterEdgeCases:
    """Test edge cases for response formatting."""

    def test_format_answer_special_characters(self):
        """Test formatting answers with special characters."""
        original = "What is C++ and JavaScript?"
        formatted = ResponseFormatter.format_answer(original)
        # Special characters and abbreviations should be preserved
        assert "C++" in formatted or "C" in formatted
        assert "JavaScript" in formatted

    def test_format_answer_very_long(self):
        """Test formatting of very long answers."""
        long_answer = "This is a very long answer. " * 100
        formatted = ResponseFormatter.format_answer(long_answer)
        # Should preserve the content and add proper punctuation
        assert formatted.startswith("This is a very long answer.")
        assert formatted.endswith(".")

    def test_format_sources_with_special_values(self):
        """Test formatting sources with special values."""
        sources = [{
            "id": "special_source",
            "title": "",
            "source": "test.md",
            "relevance_score": 0,
            "content_preview": "Normal preview",
            "chunk_index": 999
        }]

        formatted = ResponseFormatter.format_sources(sources)
        assert formatted[0]["title"] == ""
        assert formatted[0]["relevance_score"] == 0.0
        assert formatted[0]["chunk_index"] == 999

    def test_format_response_with_none_values(self):
        """Test formatting response with None values."""
        rag_response = RAGResponse(
            answer=None,
            context=None,
            sources=None,
            tokens_used=None,
            confidence=None
        )

        # This should handle None values gracefully
        formatted = ResponseFormatter.format_response_for_display(rag_response)
        assert "answer" in formatted
        assert "context" in formatted
        assert "sources" in formatted