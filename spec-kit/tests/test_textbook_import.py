import os
import tempfile
from pathlib import Path

import pytest

from src.utils.textbook_importer import TextbookImporter, ChapterData
from src.utils.frontmatter_validator import validate_frontmatter, validate_frontmatter_compliance
from src.utils.markdown_processor import MarkdownProcessor


def test_extract_frontmatter():
    """Test extracting frontmatter from markdown content."""
    content_with_frontmatter = """---
title: Introduction
id: intro
sidebar_label: Introduction
order: 1
---

# Introduction

This is the introduction chapter.
"""

    frontmatter, content_without_frontmatter = TextbookImporter.extract_frontmatter(content_with_frontmatter)

    assert frontmatter == {
        'title': 'Introduction',
        'id': 'intro',
        'sidebar_label': 'Introduction',
        'order': 1
    }

    assert "# Introduction" in content_without_frontmatter
    assert "This is the introduction chapter." in content_without_frontmatter


def test_extract_frontmatter_no_frontmatter():
    """Test extracting frontmatter when there is none."""
    content_without_frontmatter = """# Introduction

This is the introduction chapter.
"""

    frontmatter, content_without_frontmatter = TextbookImporter.extract_frontmatter(content_without_frontmatter)

    assert frontmatter == {}
    assert content_without_frontmatter == content_without_frontmatter


def test_generate_frontmatter_if_missing():
    """Test generating frontmatter when missing."""
    content = """# Introduction to AI

This chapter introduces artificial intelligence.
It covers basic concepts and principles.
"""

    generated_frontmatter = TextbookImporter.generate_frontmatter_if_missing(content, "intro.md", 1)

    assert generated_frontmatter['title'] == 'Introduction to AI'
    assert generated_frontmatter['id'] == 'intro'
    assert generated_frontmatter['sidebar_label'] == 'Introduction to AI'
    assert generated_frontmatter['order'] == 1
    assert 'This chapter introduces' in generated_frontmatter.get('description', '')


def test_frontmatter_validation():
    """Test frontmatter validation."""
    valid_frontmatter = {
        'id': 'test-chapter',
        'title': 'Test Chapter',
        'sidebar_label': 'Test Chapter',
        'order': 1
    }

    is_valid, errors = validate_frontmatter(valid_frontmatter)
    assert is_valid is True
    assert len(errors) == 0

    invalid_frontmatter = {
        'title': 'Test Chapter',  # Missing required 'id' and 'sidebar_label'
        'order': 'not-a-number'  # Wrong type for order
    }

    is_valid, errors = validate_frontmatter(invalid_frontmatter)
    assert is_valid is False
    assert len(errors) >= 2  # Should have errors for missing fields and wrong type


def test_frontmatter_compliance_validation():
    """Test Docusaurus-specific frontmatter compliance validation."""
    compliant_frontmatter = {
        'id': 'valid-id',
        'title': 'Valid Title',
        'sidebar_label': 'Valid Title',
        'order': 1,
        'draft': False
    }

    is_valid, errors = validate_frontmatter_compliance(compliant_frontmatter)
    assert is_valid is True

    non_compliant_frontmatter = {
        'id': 'invalid@id#with$special%chars',
        'title': 'Valid Title',
        'sidebar_label': 'Valid Title',
        'order': 1,
        'draft': 'not-a-boolean'  # Should be boolean
    }

    is_valid, errors = validate_frontmatter_compliance(non_compliant_frontmatter)
    assert is_valid is False
    assert len(errors) >= 1


def test_markdown_processing_extract_headings():
    """Test extracting headings from markdown."""
    content = """# Chapter Title

Some content here.

## Section 1

More content.

### Subsection 1.1

Detailed content.

## Section 2

Even more content.
"""

    headings = MarkdownProcessor.extract_headings(content)

    assert len(headings) == 4
    assert headings[0]['level'] == 1
    assert headings[0]['text'] == 'Chapter Title'
    assert headings[1]['level'] == 2
    assert headings[1]['text'] == 'Section 1'
    assert headings[2]['level'] == 3
    assert headings[2]['text'] == 'Subsection 1.1'
    assert headings[3]['level'] == 2
    assert headings[3]['text'] == 'Section 2'


def test_markdown_processing_update_image_paths():
    """Test updating image paths in markdown."""
    content = """Here is an image: ![Alt text](image.png)

And another: ![Another image](path/to/image.jpg)
"""
    new_content = MarkdownProcessor.update_image_paths(content, "/static/img")

    assert "![Alt text](/static/img/image.png)" in new_content
    assert "![Another image](/static/img/image.jpg)" in new_content


def test_markdown_processing_clean():
    """Test cleaning markdown content."""
    content = """# Title


Some content with    extra spaces.

## Section


More content.
"""
    cleaned_content = MarkdownProcessor.clean_markdown(content)

    # Should not have triple newlines
    assert "\n\n\n" not in cleaned_content
    # Should not have trailing spaces
    lines = cleaned_content.split('\n')
    for line in lines:
        assert not line.endswith('    ')  # Should not end with 4 spaces


def test_create_chapter_data():
    """Test creating ChapterData objects."""
    chapter_data = ChapterData(
        title="Test Chapter",
        content="# Test\nContent here.",
        frontmatter={"id": "test", "title": "Test Chapter", "order": 1},
        order=1,
        path="docs/test.md",
        slug="test",
        description="A test chapter"
    )

    assert chapter_data.title == "Test Chapter"
    assert "# Test" in chapter_data.content
    assert chapter_data.frontmatter["id"] == "test"
    assert chapter_data.order == 1
    assert chapter_data.path == "docs/test.md"
    assert chapter_data.slug == "test"
    assert chapter_data.description == "A test chapter"


def test_import_single_chapter():
    """Test importing a single chapter from a temporary file."""
    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""---
title: Test Chapter
id: test-chapter
sidebar_label: Test Chapter
order: 1
---

# Test Chapter

This is a test chapter.
""")
        temp_file_path = f.name

    try:
        # Import the chapter
        chapter_data = TextbookImporter.import_single_chapter(
            temp_file_path,
            order=1,
            destination_docs_dir="../my-website/docs/test/"
        )

        # Verify the imported chapter
        assert chapter_data.title == "Test Chapter"
        assert "This is a test chapter." in chapter_data.content
        assert chapter_data.frontmatter["id"] == "test-chapter"
        assert chapter_data.order == 1
        assert "test/" in chapter_data.path
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_markdown_validation():
    """Test markdown syntax validation."""
    valid_content = """# Title

This is valid markdown.

```python
print("Hello, world!")
```

- List item 1
- List item 2
"""

    is_valid, issues = MarkdownProcessor.validate_markdown_syntax(valid_content)
    assert is_valid is True
    assert len(issues) == 0

    invalid_content = """# Title

This has an unclosed code block:

```python
print("Hello, world!")
"""

    is_valid, issues = MarkdownProcessor.validate_markdown_syntax(invalid_content)
    assert is_valid is False
    assert len(issues) > 0
    assert "Unclosed code block" in issues[0]