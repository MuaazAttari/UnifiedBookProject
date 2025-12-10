from typing import List, Dict, Any
from pathlib import Path
import re


class ChapterOrderer:
    """Utility class for managing chapter ordering."""

    @staticmethod
    def order_chapters_by_filename(chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Order chapters based on filename patterns (e.g., 01-intro.md, 02-background.md).

        Args:
            chapters: List of chapter dictionaries with 'path' key

        Returns:
            List of chapters ordered by filename
        """
        def extract_number_from_filename(path: str) -> int:
            """Extract the numeric prefix from a filename."""
            filename = Path(path).name
            match = re.match(r'^(\d+)', filename)
            if match:
                return int(match.group(1))
            # If no number prefix, assign a high number to put it at the end
            return 9999

        # Sort chapters by the numeric prefix in their filenames
        return sorted(chapters, key=lambda x: extract_number_from_filename(x.get('path', '')))

    @staticmethod
    def order_chapters_by_frontmatter_order(chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Order chapters based on 'order' field in frontmatter.

        Args:
            chapters: List of chapter dictionaries with 'frontmatter' key

        Returns:
            List of chapters ordered by frontmatter order
        """
        def get_order_value(chapter: Dict[str, Any]) -> int:
            """Get the order value from frontmatter, defaulting to 9999."""
            frontmatter = chapter.get('frontmatter', {})
            return frontmatter.get('order', 9999)

        return sorted(chapters, key=lambda x: get_order_value(x))

    @staticmethod
    def order_chapters_by_title(chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Order chapters alphabetically by title.

        Args:
            chapters: List of chapter dictionaries with 'frontmatter' key containing 'title'

        Returns:
            List of chapters ordered alphabetically by title
        """
        def get_title(chapter: Dict[str, Any]) -> str:
            """Get the title from frontmatter, defaulting to empty string."""
            frontmatter = chapter.get('frontmatter', {})
            return frontmatter.get('title', '').lower()

        return sorted(chapters, key=lambda x: get_title(x))

    @staticmethod
    def apply_custom_ordering(chapters: List[Dict[str, Any]], order_list: List[str]) -> List[Dict[str, Any]]:
        """
        Order chapters according to a custom order list.

        Args:
            chapters: List of chapter dictionaries with 'slug' or 'frontmatter.id' key
            order_list: List of slugs/IDs in the desired order

        Returns:
            List of chapters ordered according to the custom order
        """
        # Create a mapping from order_list to index for sorting
        order_map = {slug: index for index, slug in enumerate(order_list)}

        def get_custom_order(chapter: Dict[str, Any]) -> int:
            """Get the custom order index for a chapter."""
            # Try to get slug first, then fall back to frontmatter id
            slug = chapter.get('slug', '')
            if not slug:
                frontmatter = chapter.get('frontmatter', {})
                slug = frontmatter.get('id', '')

            return order_map.get(slug, 9999)  # Put unmatched items at the end

        return sorted(chapters, key=lambda x: get_custom_order(x))

    @staticmethod
    def validate_ordering(chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that chapters have a consistent ordering.

        Args:
            chapters: List of chapter dictionaries

        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'duplicates': []
        }

        # Check for duplicate order values
        order_values = []
        for chapter in chapters:
            frontmatter = chapter.get('frontmatter', {})
            order = frontmatter.get('order')
            if order is not None:
                order_values.append((order, chapter.get('title', 'Unknown')))

        # Find duplicates
        seen_orders = {}
        for order, title in order_values:
            if order in seen_orders:
                result['duplicates'].append({
                    'order': order,
                    'chapters': [seen_orders[order], title]
                })
            else:
                seen_orders[order] = title

        if result['duplicates']:
            result['is_valid'] = False
            result['errors'].append(f"Found {len(result['duplicates'])} duplicate order values")

        # Check for gaps in sequence (only if all chapters have order values)
        if order_values and all(order_val[0] is not None for order_val in order_values):
            sorted_orders = sorted([order for order, _ in order_values])
            expected_sequence = list(range(min(sorted_orders), max(sorted_orders) + 1))

            if sorted_orders != expected_sequence:
                result['warnings'].append("Order sequence has gaps or missing numbers")

        return result

    @staticmethod
    def assign_sequential_order(chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign sequential order numbers to chapters that don't have them.

        Args:
            chapters: List of chapter dictionaries

        Returns:
            List of chapters with sequential order numbers assigned
        """
        # Find the highest existing order value
        max_existing_order = 0
        for chapter in chapters:
            frontmatter = chapter.get('frontmatter', {})
            order = frontmatter.get('order', 0)
            if order and order > max_existing_order:
                max_existing_order = order

        # Assign sequential order numbers to chapters without order values
        current_order = max_existing_order + 1
        updated_chapters = []

        for chapter in chapters:
            updated_chapter = chapter.copy()
            frontmatter = chapter.get('frontmatter', {}).copy()

            # Only assign order if it doesn't already exist
            if not frontmatter.get('order'):
                frontmatter['order'] = current_order
                current_order += 1

            updated_chapter['frontmatter'] = frontmatter
            updated_chapters.append(updated_chapter)

        return updated_chapters