import re
from typing import Dict, List, Tuple
from pathlib import Path


class MarkdownProcessor:
    """Utility class for processing markdown content."""

    @staticmethod
    def extract_headings(content: str) -> List[Dict[str, str]]:
        """
        Extract all headings from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of dictionaries containing heading level and text
        """
        headings = []
        # Match markdown headings (supports levels 1-6)
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        lines = content.split('\n')

        for line in lines:
            match = re.match(heading_pattern, line.strip())
            if match:
                heading_level = len(match.group(1))
                heading_text = match.group(2).strip()
                headings.append({
                    'level': heading_level,
                    'text': heading_text,
                    'raw': match.group(0)
                })

        return headings

    @staticmethod
    def update_image_paths(content: str, new_base_path: str) -> str:
        """
        Update image paths in markdown content to point to a new base path.

        Args:
            content: Markdown content
            new_base_path: New base path for images

        Returns:
            Updated markdown content with corrected image paths
        """
        # Match markdown image syntax: ![alt text](path)
        image_pattern = r'(!\[.*?\]\()([^)]+)(\))'

        def replace_path(match):
            prefix = match.group(1)  # ![alt text](
            path = match.group(2)    # the actual path
            suffix = match.group(3)  # )

            # If the path is already absolute or a URL, don't change it
            if path.startswith(('http://', 'https://', '/', 'data:')):
                return match.group(0)

            # Otherwise, update the path
            new_path = f"{new_base_path}/{Path(path).name}"
            return f"{prefix}{new_path}{suffix}"

        return re.sub(image_pattern, replace_path, content)

    @staticmethod
    def extract_links(content: str) -> List[Dict[str, str]]:
        """
        Extract all links from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of dictionaries containing link text and URL
        """
        links = []
        # Match markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        for match in re.finditer(link_pattern, content):
            links.append({
                'text': match.group(1),
                'url': match.group(2),
                'start': match.start(),
                'end': match.end()
            })

        return links

    @staticmethod
    def convert_relative_links(content: str, base_path: str) -> str:
        """
        Convert relative links in markdown to be relative to a base path.

        Args:
            content: Markdown content
            base_path: Base path to which relative links should be made relative

        Returns:
            Updated markdown content with converted links
        """
        # Match markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        def update_link(match):
            text = match.group(1)
            url = match.group(2)

            # Only update relative links (those not starting with http/https or /)
            if not url.startswith(('http://', 'https://', '/')):
                # Convert the relative link to be relative to the new base path
                new_url = f"{base_path}/{Path(url).name}"
                return f'[{text}]({new_url})'

            return match.group(0)  # Return unchanged if absolute

        return re.sub(link_pattern, update_link, content)

    @staticmethod
    def clean_markdown(content: str) -> str:
        """
        Clean markdown content by removing extra whitespace and standardizing format.

        Args:
            content: Markdown content

        Returns:
            Cleaned markdown content
        """
        # Remove extra blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Remove trailing whitespace
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]

        return '\n'.join(cleaned_lines)

    @staticmethod
    def add_table_of_contents(content: str, max_level: int = 3) -> str:
        """
        Add a table of contents to markdown content based on headings.

        Args:
            content: Markdown content
            max_level: Maximum heading level to include in TOC

        Returns:
            Updated markdown content with table of contents
        """
        headings = MarkdownProcessor.extract_headings(content)

        # Filter headings by max level
        filtered_headings = [h for h in headings if h['level'] <= max_level]

        if not filtered_headings:
            return content

        # Generate TOC
        toc = ["## Table of Contents\n"]
        for heading in filtered_headings:
            indent = "  " * (heading['level'] - 1)
            anchor = heading['text'].lower().replace(' ', '-').replace('_', '-').replace('.', '')
            toc.append(f"{indent}- [{heading['text']}](#{anchor})")

        toc.append("")  # Empty line after TOC

        # Insert TOC after frontmatter if present, otherwise at the beginning
        lines = content.split('\n')
        if lines and lines[0] == '---':
            # Find the end of frontmatter
            try:
                second_dash_index = lines.index('---', 1)
                # Insert TOC after the closing ---
                result_lines = lines[:second_dash_index + 1] + [''] + toc + lines[second_dash_index + 1:]
            except ValueError:
                # No closing --- found, insert at beginning
                result_lines = toc + lines
        else:
            # No frontmatter, insert at beginning
            result_lines = toc + lines

        return '\n'.join(result_lines)

    @staticmethod
    def validate_markdown_syntax(content: str) -> Tuple[bool, List[str]]:
        """
        Validate basic markdown syntax.

        Args:
            content: Markdown content

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check for unclosed code blocks
        code_block_count = len(re.findall(r'^```', content, re.MULTILINE))
        if code_block_count % 2 != 0:
            issues.append("Unclosed code block (``` without matching closing ```)")

        # Check for unmatched bold/italic markers
        bold_italic_pattern = r'(\*|_){1,3}.*?(\*|_){1,3}'
        for match in re.finditer(bold_italic_pattern, content):
            text = match.group(0)
            if not re.match(r'^(\*|_){1,3}.*?(\*|_){1,3}$', text):
                issues.append(f"Potentially unmatched bold/italic markers in: {text[:50]}...")

        # Check for unmatched links
        link_pattern = r'\[([^\]]*)\]'
        for match in re.finditer(link_pattern, content):
            link_text = match.group(0)
            if not re.search(r'\[([^\]]*)\]\([^)]*\)', content[match.start():match.end()+20]):
                issues.append(f"Potentially unmatched link bracket: {link_text}")

        return len(issues) == 0, issues

    @staticmethod
    def extract_first_paragraph(content: str) -> str:
        """
        Extract the first paragraph from markdown content (excluding headings and frontmatter).

        Args:
            content: Markdown content

        Returns:
            First paragraph of content
        """
        lines = content.split('\n')
        paragraph_lines = []
        in_frontmatter = False

        # Skip frontmatter if present
        if lines and lines[0].strip() == '---':
            in_frontmatter = True
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    lines = lines[i+1:]  # Skip frontmatter
                    break
            else:
                # No closing --- found, treat as content
                lines = lines[1:]

        # Skip headings
        content_start = 0
        for i, line in enumerate(lines):
            if not line.startswith('#') and line.strip():  # First non-heading, non-empty line
                content_start = i
                break

        # Collect the first paragraph (until blank line or next heading)
        for line in lines[content_start:]:
            if line.strip() == '' or line.startswith('#'):
                break
            paragraph_lines.append(line.strip())

        return ' '.join(paragraph_lines).strip()