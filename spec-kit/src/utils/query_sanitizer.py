import re
from typing import Optional
import html
import urllib.parse


class QuerySanitizer:
    """Utility class for sanitizing and validating user queries."""

    @staticmethod
    def sanitize_query(query: str) -> str:
        """
        Sanitize a user query by removing potentially harmful content.

        Args:
            query: Raw user query

        Returns:
            Sanitized query string
        """
        if not query:
            return query

        # HTML decode to handle any encoded content
        query = html.unescape(query)

        # URL decode to handle any encoded content
        query = urllib.parse.unquote(query)

        # Remove excessive whitespace
        query = " ".join(query.split())

        # Remove potential SQL injection patterns
        # This is a basic approach - for production, use proper parameterized queries
        sql_patterns = [
            r"(?i)(union\s+select)",
            r"(?i)(drop\s+table)",
            r"(?i)(create\s+table)",
            r"(?i)(delete\s+from)",
            r"(?i)(insert\s+into)",
            r"(?i)(update\s+\w+\s+set)",
            r"(?i)(exec\s*\()",
            r"(?i)(execute\s*\()",
            r"(?i)(sp_\w+)",
            r"(?i)(xp_\w+)",
        ]

        for pattern in sql_patterns:
            query = re.sub(pattern, "", query)

        # Remove potential script tags
        query = re.sub(r"(?i)<script[^>]*>.*?</script>", "", query)
        query = re.sub(r"(?i)<script[^>]*>", "", query)

        # Remove potential JavaScript event handlers
        js_event_patterns = [
            r"(?i)(on\w+\s*=)",
            r"(?i)(javascript:)",
            r"(?i)(vbscript:)",
            r"(?i)(data:)",
        ]

        for pattern in js_event_patterns:
            query = re.sub(pattern, "", query)

        # Remove potential path traversal attempts
        query = re.sub(r"(\.\.\/)+", "", query)
        query = re.sub(r"(\.\.\\)+", "", query)

        # Remove potential command injection patterns
        cmd_injection_patterns = [
            r"(?i)(\|\||&&|;|`|\$\(.*\)|%.*%)",
        ]

        for pattern in cmd_injection_patterns:
            query = re.sub(pattern, "", query)

        # Remove excessive special characters that might be used for injection
        query = re.sub(r"[{}[\]\\]", "", query)

        # Final cleanup - remove excessive whitespace again after replacements
        query = " ".join(query.split())

        return query.strip()

    @staticmethod
    def validate_query(query: str, max_length: int = 1000) -> str:
        """
        Validate and sanitize a query with additional checks.

        Args:
            query: Raw user query
            max_length: Maximum allowed length for the query

        Returns:
            Validated and sanitized query string

        Raises:
            ValueError: If query fails validation
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Check length before sanitization
        if len(query) > max_length:
            raise ValueError(f"Query is too long (max {max_length} characters)")

        # Sanitize the query
        sanitized_query = QuerySanitizer.sanitize_query(query)

        # After sanitization, check if the query is still meaningful
        if not sanitized_query:
            raise ValueError("Query contains only invalid characters")

        # Check if sanitization significantly changed the query (potential attack)
        if len(sanitized_query) < len(query) * 0.5:  # If sanitized query is less than 50% of original
            # This might indicate a potential attack, but we'll just log for now
            # In a production system, you might want to log this for security monitoring
            pass

        return sanitized_query

    @staticmethod
    def sanitize_context(context: str) -> str:
        """
        Sanitize context text (like selected_text) to prevent injection.

        Args:
            context: Context text to sanitize

        Returns:
            Sanitized context string
        """
        if not context:
            return context

        # Apply similar sanitization as for queries
        context = html.unescape(context)
        context = urllib.parse.unquote(context)
        context = " ".join(context.split())

        # Remove potential harmful patterns but be more lenient with context
        # since it might contain legitimate code or technical content
        harmful_patterns = [
            r"(?i)<script[^>]*>.*?</script>",
            r"(?i)<script[^>]*>",
            r"(?i)(on\w+\s*=)",
            r"(?i)(javascript:)",
            r"(?i)(vbscript:)",
        ]

        for pattern in harmful_patterns:
            context = re.sub(pattern, "", context)

        # Remove path traversal attempts
        context = re.sub(r"(\.\.\/)+", "", context)
        context = re.sub(r"(\.\.\\)+", "", context)

        context = " ".join(context.split())

        return context.strip()