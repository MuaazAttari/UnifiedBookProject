import re
from typing import Dict, Any, List, Optional
from src.services.rag_service import RAGResponse


class ResponseFormatter:
    """Utility class for formatting and post-processing RAG responses."""

    @staticmethod
    def format_answer(answer: str) -> str:
        """
        Format the answer text with basic cleanup and standardization.

        Args:
            answer: Raw answer text from the LLM

        Returns:
            Formatted answer text
        """
        if not answer:
            return answer

        # Remove excessive whitespace
        answer = " ".join(answer.split())

        # Ensure proper capitalization for the first character
        if answer and answer[0].isalpha():
            answer = answer[0].upper() + answer[1:]

        # Clean up common formatting issues from LLM responses
        # Remove common prefixes like "Answer:", "Response:", etc.
        answer = re.sub(r"^(Answer|Response|Question):\s*", "", answer, flags=re.IGNORECASE)

        # Ensure the answer ends with proper punctuation
        if answer and not answer.endswith(('.', '!', '?', '."', '."')):
            # Check if it ends with a quote
            if not answer.endswith('"'):
                answer += '.'

        return answer.strip()

    @staticmethod
    def format_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format the sources information for consistency.

        Args:
            sources: List of source dictionaries

        Returns:
            Formatted list of sources
        """
        formatted_sources = []
        for source in sources:
            formatted_source = {
                "id": source.get("id", ""),
                "title": source.get("title", ""),
                "source": source.get("source", ""),
                "relevance_score": float(source.get("relevance_score", 0)),
                "content_preview": source.get("content_preview", ""),
                "chunk_index": source.get("chunk_index", 0)
            }
            formatted_sources.append(formatted_source)

        return formatted_sources

    @staticmethod
    def format_response_for_display(response: RAGResponse) -> Dict[str, Any]:
        """
        Format the complete RAG response for display purposes.

        Args:
            response: RAGResponse object

        Returns:
            Dictionary with formatted response data
        """
        formatted_answer = ResponseFormatter.format_answer(response.answer)
        formatted_sources = ResponseFormatter.format_sources(response.sources)

        formatted_response = {
            "answer": formatted_answer,
            "context": response.context,
            "sources": formatted_sources,
            "tokens_used": response.tokens_used,
            "confidence": round(response.confidence, 3),  # Round to 3 decimal places
            "formatted": True  # Flag to indicate this response has been formatted
        }

        return formatted_response

    @staticmethod
    def add_citations_to_answer(answer: str, sources: List[Dict[str, Any]]) -> str:
        """
        Add citation markers to the answer text linking to sources.

        Args:
            answer: The answer text
            sources: List of sources

        Returns:
            Answer text with citation markers
        """
        if not sources:
            return answer

        # For now, we'll add a simple citation at the end
        # In a more sophisticated implementation, we could use NLP to identify
        # which parts of the answer come from which sources
        citation_text = f"\n\nBased on information from {len(sources)} source{'s' if len(sources) != 1 else ''}:"
        for i, source in enumerate(sources):
            title = source.get("title", "Unknown Source")
            citation_text += f"\n[{i+1}] {title}"

        return answer + citation_text

    @staticmethod
    def post_process_response(response: RAGResponse, add_citations: bool = True) -> Dict[str, Any]:
        """
        Complete post-processing of a RAG response.

        Args:
            response: RAGResponse object
            add_citations: Whether to add citations to the answer

        Returns:
            Fully processed response dictionary
        """
        # Format the answer
        formatted_answer = ResponseFormatter.format_answer(response.answer)

        # Add citations if requested
        if add_citations:
            formatted_answer = ResponseFormatter.add_citations_to_answer(formatted_answer, response.sources)

        # Format sources
        formatted_sources = ResponseFormatter.format_sources(response.sources)

        # Create the final processed response
        processed_response = {
            "answer": formatted_answer,
            "context": response.context,
            "sources": formatted_sources,
            "tokens_used": response.tokens_used,
            "confidence": round(response.confidence, 3),
            "confidence_percentage": round(response.confidence * 100, 1),
            "processed": True
        }

        return processed_response

    @staticmethod
    def sanitize_response_content(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize response content to prevent XSS or other injection issues.

        Args:
            response_data: Response data dictionary

        Returns:
            Sanitized response data
        """
        import html
        import urllib.parse

        sanitized = response_data.copy()

        # Sanitize the answer
        if "answer" in sanitized and sanitized["answer"]:
            sanitized["answer"] = html.escape(sanitized["answer"])

        # Sanitize context
        if "context" in sanitized and sanitized["context"]:
            sanitized["context"] = html.escape(sanitized["context"])

        # Sanitize sources
        if "sources" in sanitized and isinstance(sanitized["sources"], list):
            for source in sanitized["sources"]:
                if "title" in source and source["title"]:
                    source["title"] = html.escape(str(source["title"]))
                if "content_preview" in source and source["content_preview"]:
                    source["content_preview"] = html.escape(str(source["content_preview"]))

        return sanitized