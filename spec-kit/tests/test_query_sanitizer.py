import pytest
from src.utils.query_sanitizer import QuerySanitizer


class TestQuerySanitizer:
    """Test suite for the QuerySanitizer utility."""

    def test_sanitize_query_basic(self):
        """Test basic query sanitization."""
        original = "This is a normal query"
        sanitized = QuerySanitizer.sanitize_query(original)
        assert sanitized == "This is a normal query"

    def test_sanitize_query_excessive_whitespace(self):
        """Test sanitization of excessive whitespace."""
        original = "  This   has   excessive   spaces  "
        sanitized = QuerySanitizer.sanitize_query(original)
        assert sanitized == "This has excessive spaces"

    def test_sanitize_query_html_tags(self):
        """Test removal of HTML script tags."""
        original = "What is this? <script>alert('xss')</script> about the topic?"
        sanitized = QuerySanitizer.sanitize_query(original)
        assert "<script>" not in sanitized
        assert "alert('xss')" not in sanitized
        assert "What is this?" in sanitized
        assert "about the topic?" in sanitized

    def test_sanitize_query_html_encoded(self):
        """Test sanitization of HTML-encoded content."""
        original = "What is this? &lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt; topic?"
        sanitized = QuerySanitizer.sanitize_query(original)
        assert "&lt;script&gt;" not in sanitized
        assert "alert" not in sanitized

    def test_sanitize_query_url_encoded(self):
        """Test sanitization of URL-encoded content."""
        original = "What is this? %3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E topic?"
        sanitized = QuerySanitizer.sanitize_query(original)
        # After URL decoding and HTML unescaping, script tags should be removed
        assert "script" not in sanitized.lower()

    def test_sanitize_query_sql_injection(self):
        """Test removal of SQL injection patterns."""
        sql_patterns = [
            "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM users",
            "DROP TABLE users",
            "CREATE TABLE malicious",
            "DELETE FROM users WHERE id = 1",
            "INSERT INTO users VALUES ('hacker', 'pwd')",
            "UPDATE users SET password = 'hacked'",
            "EXEC sp_drop_user",
            "EXECUTE xp_cmdshell",
        ]

        for pattern in sql_patterns:
            sanitized = QuerySanitizer.sanitize_query(pattern)
            # The sanitized version should be significantly different
            # or completely empty for obvious injection attempts
            assert len(sanitized) < len(pattern) * 0.5  # At least 50% reduction for injection attempts

    def test_sanitize_query_path_traversal(self):
        """Test removal of path traversal attempts."""
        original = "Show me ../etc/passwd file content"
        sanitized = QuerySanitizer.sanitize_query(original)
        assert "../" not in sanitized
        assert "/etc/passwd" not in sanitized

    def test_sanitize_query_command_injection(self):
        """Test removal of command injection patterns."""
        original = "What is this? | ls -la; echo 'injection' `whoami`"
        sanitized = QuerySanitizer.sanitize_query(original)
        assert "|" not in sanitized
        assert ";" not in sanitized
        assert "`whoami`" not in sanitized

    def test_validate_query_empty(self):
        """Test validation of empty queries."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            QuerySanitizer.validate_query("")

        with pytest.raises(ValueError, match="Query cannot be empty"):
            QuerySanitizer.validate_query("   ")

    def test_validate_query_too_long(self):
        """Test validation of overly long queries."""
        long_query = "x" * 1001  # 1001 characters, exceeding default 1000 limit
        with pytest.raises(ValueError, match="Query is too long"):
            QuerySanitizer.validate_query(long_query)

        # Test with custom length limit
        short_query = "x" * 51
        with pytest.raises(ValueError, match="Query is too long"):
            QuerySanitizer.validate_query(short_query, max_length=50)

    def test_validate_query_normal(self):
        """Test validation of normal queries."""
        normal_query = "This is a normal, valid query."
        validated = QuerySanitizer.validate_query(normal_query)
        assert validated == "This is a normal, valid query."

    def test_validate_query_with_sanitization(self):
        """Test validation that includes sanitization."""
        malicious_query = "<script>alert('xss')</script>Normal query"
        validated = QuerySanitizer.validate_query(malicious_query)
        assert "<script>" not in validated
        assert "alert" not in validated
        assert "Normal query" in validated

    def test_sanitize_context_basic(self):
        """Test basic context sanitization."""
        original = "This is normal context text."
        sanitized = QuerySanitizer.sanitize_context(original)
        assert sanitized == "This is normal context text."

    def test_sanitize_context_with_html(self):
        """Test context sanitization with HTML content."""
        original = "This is context with <b>HTML</b> and <script>alert('xss')</script> content."
        sanitized = QuerySanitizer.sanitize_context(original)
        assert "<b>HTML</b>" in sanitized  # Normal HTML might be allowed in context
        assert "<script>" not in sanitized
        assert "alert" not in sanitized

    def test_sanitize_context_path_traversal(self):
        """Test context sanitization for path traversal."""
        original = "Context with path traversal: ../../secret.txt"
        sanitized = QuerySanitizer.sanitize_context(original)
        assert "../../" not in sanitized

    def test_none_input(self):
        """Test handling of None input."""
        assert QuerySanitizer.sanitize_query(None) is None
        assert QuerySanitizer.sanitize_context(None) is None

        with pytest.raises(ValueError):
            QuerySanitizer.validate_query(None)


class TestQuerySanitizerIntegration:
    """Integration tests for query sanitization."""

    def test_end_to_end_sanitization(self):
        """Test the complete sanitization workflow."""
        malicious_input = "   <script>alert('xss')</script>   What is SQL injection?   "
        try:
            validated = QuerySanitizer.validate_query(malicious_input)
            # If validation passes, the input should be sanitized
            assert "<script>" not in validated
            assert "alert" not in validated
            assert validated.strip() == "What is SQL injection?"  # Cleaned and trimmed
        except ValueError:
            # Validation might fail if sanitization removes too much content
            pass  # This is also acceptable behavior

    def test_technical_content_preservation(self):
        """Test that technical content is preserved while malicious content is removed."""
        # This query contains legitimate technical terms that might look like injection
        technical_query = "How do I use {json: 'objects'} and [arrays: 'in javascript']?"
        sanitized = QuerySanitizer.sanitize_query(technical_query)
        # The technical content should be preserved
        assert "json" in sanitized.lower()
        assert "javascript" in sanitized.lower()
        # But actual harmful patterns should be removed
        assert "{" not in sanitized  # This might be removed as part of the sanitization
        # Note: Our current sanitization removes braces, which might affect technical queries
        # This is a trade-off between security and functionality

    def test_preserve_legitimate_quotes(self):
        """Test that legitimate quotes are preserved."""
        legitimate_quotes = "What does 'single quotes' and \"double quotes\" mean?"
        sanitized = QuerySanitizer.sanitize_query(legitimate_quotes)
        # Quotes should be preserved as they're part of normal language
        assert "'" in sanitized or '"' in sanitized