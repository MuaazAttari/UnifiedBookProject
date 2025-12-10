import json
import tempfile
import os
from pathlib import Path

import pytest

from src.utils.sidebars_generator import SidebarsGenerator


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

    frontmatter = SidebarsGenerator._extract_frontmatter(content_with_frontmatter)

    assert frontmatter == {
        'title': 'Introduction',
        'id': 'intro',
        'sidebar_label': 'Introduction',
        'order': 1
    }


def test_extract_frontmatter_no_frontmatter():
    """Test extracting frontmatter when there is none."""
    content_without_frontmatter = """# Introduction

This is the introduction chapter.
"""

    frontmatter = SidebarsGenerator._extract_frontmatter(content_without_frontmatter)

    assert frontmatter == {}


def test_generate_sidebar_from_filesystem():
    """Test generating sidebar configuration from filesystem."""
    # Create a temporary directory with markdown files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test markdown files with frontmatter
        chapter1_content = """---
title: Introduction
id: intro
sidebar_label: Introduction
order: 1
---

# Introduction

This is the introduction chapter.
"""

        chapter2_content = """---
title: Background
id: background
sidebar_label: Background
order: 2
---

# Background

This is the background chapter.
"""

        # Write test files
        chapter1_path = Path(temp_dir) / "intro.md"
        chapter2_path = Path(temp_dir) / "background.md"

        with open(chapter1_path, 'w', encoding='utf-8') as f:
            f.write(chapter1_content)

        with open(chapter2_path, 'w', encoding='utf-8') as f:
            f.write(chapter2_content)

        # Generate sidebar from filesystem
        sidebar_config = SidebarsGenerator.generate_sidebar_from_filesystem(temp_dir)

        # Verify the configuration
        assert 'tutorialSidebar' in sidebar_config
        sidebar_items = sidebar_config['tutorialSidebar']

        assert len(sidebar_items) == 2
        assert sidebar_items[0]['id'] == 'intro'
        assert sidebar_items[0]['label'] == 'Introduction'
        assert sidebar_items[1]['id'] == 'background'
        assert sidebar_items[1]['label'] == 'Background'


def test_save_sidebar_config():
    """Test saving sidebar configuration to file."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "sidebars.js"

        # Create a test sidebar configuration
        test_config = {
            "tutorialSidebar": [
                {
                    "type": "doc",
                    "id": "intro",
                    "label": "Introduction"
                },
                {
                    "type": "doc",
                    "id": "background",
                    "label": "Background"
                }
            ]
        }

        # Save the configuration
        SidebarsGenerator.save_sidebar_config(test_config, str(output_path))

        # Verify the file was created and has correct content
        assert output_path.exists()

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check that the file contains expected elements
        assert "const sidebars = " in content
        assert '"intro"' in content
        assert '"background"' in content
        assert "module.exports = sidebars;" in content


def test_sidebar_generation_with_missing_order():
    """Test sidebar generation when some files have missing order values."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test markdown files with and without order
        chapter1_content = """---
title: Introduction
id: intro
sidebar_label: Introduction
order: 1
---

# Introduction
"""

        chapter2_content = """---
title: No Order Chapter
id: no-order
sidebar_label: No Order Chapter
---

# No Order Chapter
"""

        chapter3_content = """---
title: Conclusion
id: conclusion
sidebar_label: Conclusion
order: 3
---

# Conclusion
"""

        # Write test files
        chapter1_path = Path(temp_dir) / "intro.md"
        chapter2_path = Path(temp_dir) / "no-order.md"
        chapter3_path = Path(temp_dir) / "conclusion.md"

        with open(chapter1_path, 'w', encoding='utf-8') as f:
            f.write(chapter1_content)

        with open(chapter2_path, 'w', encoding='utf-8') as f:
            f.write(chapter2_content)

        with open(chapter3_path, 'w', encoding='utf-8') as f:
            f.write(chapter3_content)

        # Generate sidebar from filesystem
        sidebar_config = SidebarsGenerator.generate_sidebar_from_filesystem(temp_dir)

        # Verify the configuration - the no-order chapter should appear last
        sidebar_items = sidebar_config['tutorialSidebar']
        assert len(sidebar_items) == 3
        assert sidebar_items[0]['id'] == 'intro'  # order: 1
        assert sidebar_items[2]['id'] == 'conclusion'  # order: 3
        # The no-order chapter could be at position 1 or 2 depending on file system order,
        # but it should not be first since 'intro' has order 1


def test_sidebar_generation_empty_directory():
    """Test sidebar generation with an empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate sidebar from empty directory
        sidebar_config = SidebarsGenerator.generate_sidebar_from_filesystem(temp_dir)

        # Verify the configuration is valid
        assert 'tutorialSidebar' in sidebar_config
        sidebar_items = sidebar_config['tutorialSidebar']
        assert sidebar_items == []  # Should be empty list


def test_sidebar_generation_nonexistent_directory():
    """Test sidebar generation with a nonexistent directory."""
    with pytest.raises(FileNotFoundError):
        SidebarsGenerator.generate_sidebar_from_filesystem("/nonexistent/directory")


def test_autogenerated_sidebar_fallback():
    """Test that the system creates an autogenerated sidebar when no files exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a markdown file without frontmatter
        test_file = Path(temp_dir) / "test.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Test Chapter\n\nContent here.")

        # Generate sidebar
        sidebar_config = SidebarsGenerator.generate_sidebar_from_filesystem(temp_dir)

        # Verify configuration
        assert 'tutorialSidebar' in sidebar_config
        sidebar_items = sidebar_config['tutorialSidebar']
        assert len(sidebar_items) == 1
        assert sidebar_items[0]['id'] == 'test'