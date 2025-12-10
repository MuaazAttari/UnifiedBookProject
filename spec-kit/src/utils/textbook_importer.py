import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

import yaml

from src.utils.frontmatter_validator import validate_frontmatter


@dataclass
class ChapterData:
    """Data class to represent a chapter during import."""
    title: str
    content: str
    frontmatter: Dict
    order: int
    path: str
    slug: str
    description: Optional[str] = None


class TextbookImporter:
    """Utility class for importing textbook content."""

    @staticmethod
    def extract_frontmatter(content: str) -> tuple:
        """
        Extract frontmatter from markdown content.

        Args:
            content: Markdown content with potential frontmatter

        Returns:
            Tuple of (frontmatter dict, content without frontmatter)
        """
        # Look for YAML frontmatter between --- delimiters
        pattern = r'^---\n(.*?)\n---\n(.*)'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            frontmatter_yaml = match.group(1)
            content_without_frontmatter = match.group(2)

            try:
                frontmatter = yaml.safe_load(frontmatter_yaml)
                if frontmatter is None:
                    frontmatter = {}
            except yaml.YAMLError:
                # If YAML parsing fails, treat as no frontmatter
                return {}, content
        else:
            # No frontmatter found
            frontmatter = {}
            content_without_frontmatter = content

        return frontmatter, content_without_frontmatter

    @staticmethod
    def generate_frontmatter_if_missing(content: str, filename: str, order: int) -> Dict:
        """
        Generate basic frontmatter if missing.

        Args:
            content: Markdown content
            filename: Name of the file being processed
            order: Order of the chapter

        Returns:
            Generated frontmatter dictionary
        """
        # Extract title from first heading or filename
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Use filename without extension as title
            title = Path(filename).stem.replace('_', ' ').replace('-', ' ').title()

        # Generate slug from filename
        slug = Path(filename).stem.lower()

        # Extract first sentence as description
        lines = content.split('\n')
        description = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove markdown formatting from description
                description = re.sub(r'\*|\`|\[|\]|\(|\)', '', line)
                if len(description) > 100:
                    description = description[:97] + "..."
                break

        return {
            "id": slug,
            "title": title,
            "sidebar_label": title,
            "description": description,
            "order": order
        }

    @staticmethod
    def import_chapters_from_directory(
        source_dir: str,
        destination_docs_dir: str = "../my-website/docs/physical-ai/",
        chapter_prefix: str = "0"
    ) -> List[ChapterData]:
        """
        Import all markdown chapters from a directory.

        Args:
            source_dir: Directory containing source markdown files
            destination_docs_dir: Destination directory for docs
            chapter_prefix: Prefix for chapter numbering

        Returns:
            List of ChapterData objects
        """
        chapters = []
        source_path = Path(source_dir)

        if not source_path.exists():
            raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

        # Get all markdown files and sort them
        md_files = sorted(list(source_path.glob("*.md")) + list(source_path.glob("*.mdx")))

        for idx, file_path in enumerate(md_files, 1):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract or generate frontmatter
            frontmatter, content_without_frontmatter = TextbookImporter.extract_frontmatter(content)

            # If no frontmatter exists, generate it
            if not frontmatter:
                frontmatter = TextbookImporter.generate_frontmatter_if_missing(
                    content, file_path.name, idx
                )

            # Ensure required frontmatter fields exist
            if 'id' not in frontmatter:
                frontmatter['id'] = Path(file_path).stem.lower()
            if 'title' not in frontmatter:
                frontmatter['title'] = Path(file_path).stem.replace('_', ' ').title()
            if 'sidebar_label' not in frontmatter:
                frontmatter['sidebar_label'] = frontmatter['title']
            if 'order' not in frontmatter:
                frontmatter['order'] = idx

            # Validate frontmatter
            is_valid, errors = validate_frontmatter(frontmatter)
            if not is_valid:
                print(f"Warning: Frontmatter validation failed for {file_path.name}: {errors}")

            # Generate slug
            slug = frontmatter.get('id', Path(file_path).stem.lower())

            # Determine destination path
            relative_path = f"{destination_docs_dir}{file_path.name}"

            chapter_data = ChapterData(
                title=frontmatter['title'],
                content=content_without_frontmatter,
                frontmatter=frontmatter,
                order=frontmatter['order'],
                path=relative_path,
                slug=slug,
                description=frontmatter.get('description', '')
            )

            chapters.append(chapter_data)

        return chapters

    @staticmethod
    def import_single_chapter(
        file_path: str,
        order: int,
        destination_docs_dir: str = "../my-website/docs/physical-ai/"
    ) -> ChapterData:
        """
        Import a single chapter from a file.

        Args:
            file_path: Path to the markdown file
            order: Order of the chapter
            destination_docs_dir: Destination directory for docs

        Returns:
            ChapterData object
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract or generate frontmatter
        frontmatter, content_without_frontmatter = TextbookImporter.extract_frontmatter(content)

        # If no frontmatter exists, generate it
        if not frontmatter:
            frontmatter = TextbookImporter.generate_frontmatter_if_missing(
                content, path.name, order
            )

        # Ensure required frontmatter fields exist
        if 'id' not in frontmatter:
            frontmatter['id'] = Path(path).stem.lower()
        if 'title' not in frontmatter:
            frontmatter['title'] = Path(path).stem.replace('_', ' ').title()
        if 'sidebar_label' not in frontmatter:
            frontmatter['sidebar_label'] = frontmatter['title']
        if 'order' not in frontmatter:
            frontmatter['order'] = order

        # Validate frontmatter
        is_valid, errors = validate_frontmatter(frontmatter)
        if not is_valid:
            print(f"Warning: Frontmatter validation failed for {path.name}: {errors}")

        # Generate slug
        slug = frontmatter.get('id', Path(path).stem.lower())

        # Determine destination path
        relative_path = f"{destination_docs_dir}{path.name}"

        return ChapterData(
            title=frontmatter['title'],
            content=content_without_frontmatter,
            frontmatter=frontmatter,
            order=frontmatter['order'],
            path=relative_path,
            slug=slug,
            description=frontmatter.get('description', '')
        )

    @staticmethod
    def save_chapters_to_directory(chapters: List[ChapterData], output_dir: str) -> None:
        """
        Save chapters to a directory as markdown files.

        Args:
            chapters: List of ChapterData objects to save
            output_dir: Directory to save the files to
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for chapter in chapters:
            # Create frontmatter string
            frontmatter_str = yaml.dump(chapter.frontmatter, default_flow_style=False)

            # Combine frontmatter and content
            full_content = f"---\n{frontmatter_str}---\n\n{chapter.content}"

            # Write to file
            file_path = output_path / f"{chapter.slug}.md"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)

        print(f"Saved {len(chapters)} chapters to {output_dir}")


class ImportStatusReporter:
    """Utility class for reporting import status and statistics."""

    @staticmethod
    def generate_import_report(
        source_dir: str,
        imported_chapters: List[ChapterData],
        failed_files: List[str] = None,
        warnings: List[str] = None
    ) -> Dict[str, any]:
        """
        Generate a comprehensive import status report.

        Args:
            source_dir: Source directory of the import
            imported_chapters: List of successfully imported chapters
            failed_files: List of files that failed to import
            warnings: List of warnings during import

        Returns:
            Dictionary containing import statistics and status
        """
        report = {
            'summary': {
                'source_directory': source_dir,
                'total_files_processed': len(imported_chapters) + (len(failed_files) if failed_files else 0),
                'successful_imports': len(imported_chapters),
                'failed_imports': len(failed_files) if failed_files else 0,
                'warnings_count': len(warnings) if warnings else 0,
                'status': 'completed_with_issues' if (failed_files or warnings) else 'completed_successfully'
            },
            'chapters': [],
            'errors': failed_files or [],
            'warnings': warnings or [],
            'statistics': {}
        }

        # Chapter details
        for chapter in imported_chapters:
            report['chapters'].append({
                'title': chapter.title,
                'slug': chapter.slug,
                'path': chapter.path,
                'order': chapter.order,
                'word_count': len(chapter.content.split()),
                'has_frontmatter': bool(chapter.frontmatter)
            })

        # Statistics
        if imported_chapters:
            report['statistics'] = {
                'total_word_count': sum(len(chapter.content.split()) for chapter in imported_chapters),
                'avg_word_count': sum(len(chapter.content.split()) for chapter in imported_chapters) / len(imported_chapters),
                'min_order': min(chapter.order for chapter in imported_chapters),
                'max_order': max(chapter.order for chapter in imported_chapters),
                'order_range': max(chapter.order for chapter in imported_chapters) - min(chapter.order for chapter in imported_chapters) + 1
            }

        return report

    @staticmethod
    def print_import_summary(report: Dict[str, any]) -> None:
        """
        Print a formatted import summary to the console.

        Args:
            report: Import report dictionary
        """
        summary = report['summary']
        stats = report['statistics']

        print("="*50)
        print("TEXTBOOK IMPORT SUMMARY")
        print("="*50)
        print(f"Source Directory: {summary['source_directory']}")
        print(f"Status: {summary['status'].replace('_', ' ').title()}")
        print(f"Files Processed: {summary['total_files_processed']}")
        print(f"Successful Imports: {summary['successful_imports']}")
        print(f"Failed Imports: {summary['failed_imports']}")
        print(f"Warnings: {summary['warnings_count']}")
        print("-"*50)

        if stats:
            print(f"Total Words: {stats.get('total_word_count', 0):,}")
            print(f"Average Words per Chapter: {stats.get('avg_word_count', 0):.0f}")
            print(f"Chapter Order Range: {stats.get('min_order', 0)} - {stats.get('max_order', 0)}")

        if report['errors']:
            print("\nFAILED FILES:")
            for error in report['errors']:
                print(f"  - {error}")

        if report['warnings']:
            print("\nWARNINGS:")
            for warning in report['warnings']:
                print(f"  - {warning}")

        print("="*50)