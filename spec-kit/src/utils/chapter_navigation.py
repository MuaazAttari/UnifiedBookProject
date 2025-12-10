from typing import List, Dict, Optional
from pathlib import Path


class ChapterNavigation:
    """Utility class for managing navigation links between chapters."""

    @staticmethod
    def add_navigation_links_to_chapters(
        chapters: List[Dict],
        base_url: str = "/docs/physical-ai/"
    ) -> List[Dict]:
        """
        Add navigation links (previous, next) to chapters based on their order.

        Args:
            chapters: List of chapter dictionaries with 'order' and 'slug' fields
            base_url: Base URL for the documentation

        Returns:
            List of chapters with navigation links added
        """
        # Sort chapters by order
        sorted_chapters = sorted(
            chapters,
            key=lambda x: x.get('order', 9999)
        )

        # Add navigation links to each chapter
        for i, chapter in enumerate(sorted_chapters):
            # Add previous link
            if i > 0:
                prev_chapter = sorted_chapters[i - 1]
                chapter['prev'] = {
                    'title': prev_chapter.get('title', ''),
                    'url': f"{base_url}{prev_chapter.get('slug', '')}"
                }

            # Add next link
            if i < len(sorted_chapters) - 1:
                next_chapter = sorted_chapters[i + 1]
                chapter['next'] = {
                    'title': next_chapter.get('title', ''),
                    'url': f"{base_url}{next_chapter.get('slug', '')}"
                }

        return sorted_chapters

    @staticmethod
    def generate_navigation_markdown(
        chapter: Dict,
        template: Optional[str] = None
    ) -> str:
        """
        Generate navigation markdown to add to the end of a chapter.

        Args:
            chapter: Chapter dictionary with navigation links
            template: Optional custom template for navigation

        Returns:
            Markdown string with navigation links
        """
        if template is None:
            template = """
<div className="chapter-nav">
  {prev_link}
  {next_link}
</div>
"""

        prev_link = ""
        next_link = ""

        if chapter.get('prev'):
            prev = chapter['prev']
            prev_link = f'<div className="prev"><a href="{prev["url"]}">← {prev["title"]}</a></div>'

        if chapter.get('next'):
            next_item = chapter['next']
            next_link = f'<div className="next"><a href="{next_item["url"]}">{next_item["title"]} →</a></div>'

        # Replace placeholders in template
        nav_md = template.format(prev_link=prev_link, next_link=next_link)

        return nav_md

    @staticmethod
    def add_navigation_to_markdown_content(
        content: str,
        chapter: Dict,
        position: str = "end"
    ) -> str:
        """
        Add navigation links to markdown content.

        Args:
            content: Original markdown content
            chapter: Chapter dictionary with navigation links
            position: Where to add navigation ('start', 'end', or 'both')

        Returns:
            Updated markdown content with navigation
        """
        navigation_md = ChapterNavigation.generate_navigation_markdown(chapter)

        if position == "start":
            return navigation_md + "\n\n" + content
        elif position == "end":
            return content + "\n\n" + navigation_md
        elif position == "both":
            return navigation_md + "\n\n" + content + "\n\n" + navigation_md
        else:
            return content  # Default to not adding navigation

    @staticmethod
    def update_chapter_files_with_navigation(
        chapters_dir: str,
        updated_chapters: List[Dict],
        base_url: str = "/docs/physical-ai/"
    ) -> None:
        """
        Update markdown files in a directory with navigation links.

        Args:
            chapters_dir: Directory containing chapter markdown files
            updated_chapters: List of chapters with navigation links
            base_url: Base URL for the documentation
        """
        import os

        # Create a mapping from slug to chapter for quick lookup
        chapter_map = {ch.get('slug', ''): ch for ch in updated_chapters}

        # Process each file in the directory
        for filename in os.listdir(chapters_dir):
            if filename.endswith(('.md', '.mdx')):
                slug = Path(filename).stem
                if slug in chapter_map:
                    chapter = chapter_map[slug]

                    # Read the current content
                    filepath = os.path.join(chapters_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Add navigation to the content
                    updated_content = ChapterNavigation.add_navigation_to_markdown_content(
                        content, chapter, position="end"
                    )

                    # Write the updated content back
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

                    print(f"Updated navigation for {filename}")

    @staticmethod
    def generate_table_of_contents(
        chapters: List[Dict],
        max_level: int = 2,
        include_navigation: bool = True
    ) -> str:
        """
        Generate a table of contents for the book.

        Args:
            chapters: List of chapters with order and title
            max_level: Maximum heading level for TOC
            include_navigation: Whether to include navigation links

        Returns:
            Markdown string for table of contents
        """
        # Sort chapters by order
        sorted_chapters = sorted(
            chapters,
            key=lambda x: x.get('order', 9999)
        )

        toc_lines = ["# Table of Contents\n"]
        for chapter in sorted_chapters:
            indent = "  " * (chapter.get('level', 1) - 1)
            slug = chapter.get('slug', '')
            title = chapter.get('title', 'Untitled Chapter')
            toc_lines.append(f"{indent}- [{title}](./{slug})")

        if include_navigation:
            toc_lines.append("\n-------------------\n")
            toc_lines.append("← [Introduction](./intro) | [Chapter 1](./chapter-1) →")

        return "\n".join(toc_lines)

    @staticmethod
    def create_navigation_json(
        chapters: List[Dict],
        output_file: str = "../my-website/src/data/navigation.json"
    ) -> None:
        """
        Create a navigation JSON file that can be used by the frontend.

        Args:
            chapters: List of chapters with navigation links
            output_file: Path to save the navigation JSON
        """
        import json

        # Sort chapters by order
        sorted_chapters = sorted(
            chapters,
            key=lambda x: x.get('order', 9999)
        )

        # Create navigation structure
        nav_structure = {
            "chapters": []
        }

        for i, chapter in enumerate(sorted_chapters):
            nav_item = {
                "id": chapter.get('slug', ''),
                "title": chapter.get('title', ''),
                "order": chapter.get('order', i),
                "url": chapter.get('path', f"/docs/{chapter.get('slug', '')}")
            }

            # Add prev/next if they exist in the sorted list
            if i > 0:
                nav_item["prev"] = {
                    "id": sorted_chapters[i-1].get('slug', ''),
                    "title": sorted_chapters[i-1].get('title', ''),
                    "url": sorted_chapters[i-1].get('path', f"/docs/{sorted_chapters[i-1].get('slug', '')}")
                }

            if i < len(sorted_chapters) - 1:
                nav_item["next"] = {
                    "id": sorted_chapters[i+1].get('slug', ''),
                    "title": sorted_chapters[i+1].get('title', ''),
                    "url": sorted_chapters[i+1].get('path', f"/docs/{sorted_chapters[i+1].get('slug', '')}")
                }

            nav_structure["chapters"].append(nav_item)

        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(nav_structure, f, indent=2)

        print(f"Navigation JSON saved to {output_file}")