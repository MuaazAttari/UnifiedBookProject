import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
import re

from PIL import Image


class AssetManager:
    """Utility class for managing assets (images, documents, etc.) for the Docusaurus site."""

    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    SUPPORTED_DOC_FORMATS = {'.pdf', '.doc', '.docx', '.txt', '.md'}

    @staticmethod
    def get_file_hash(filepath: str) -> str:
        """
        Generate a hash for a file to detect duplicates.

        Args:
            filepath: Path to the file

        Returns:
            SHA256 hash of the file
        """
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    @staticmethod
    def find_assets_in_directory(
        directory: str,
        extensions: Optional[List[str]] = None
    ) -> List[str]:
        """
        Find all assets in a directory with specified extensions.

        Args:
            directory: Directory to search in
            extensions: List of file extensions to look for (e.g., ['.jpg', '.png'])

        Returns:
            List of file paths
        """
        if extensions is None:
            extensions = list(AssetManager.SUPPORTED_IMAGE_FORMATS)

        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {directory}")

        assets = []
        for ext in extensions:
            # Find files with the specified extension (case insensitive)
            pattern = f"*.{ext[1:]}"  # Remove the dot from extension
            assets.extend(directory_path.rglob(pattern))
            # Also look for uppercase extensions
            pattern_upper = f"*.{ext[1:].upper()}"
            if pattern != pattern_upper:
                assets.extend(directory_path.rglob(pattern_upper))

        # Convert to strings and return
        return [str(asset) for asset in assets]

    @staticmethod
    def copy_asset_to_destination(
        source_path: str,
        destination_dir: str,
        preserve_filename: bool = True,
        add_hash: bool = False
    ) -> str:
        """
        Copy an asset to the destination directory.

        Args:
            source_path: Path to the source file
            destination_dir: Destination directory
            preserve_filename: Whether to preserve the original filename
            add_hash: Whether to add a hash to avoid conflicts

        Returns:
            Path to the copied file
        """
        source_path_obj = Path(source_path)
        destination_dir_obj = Path(destination_dir)

        # Create destination directory if it doesn't exist
        destination_dir_obj.mkdir(parents=True, exist_ok=True)

        if preserve_filename:
            if add_hash:
                # Add hash to filename to avoid conflicts
                file_hash = AssetManager.get_file_hash(source_path)
                stem = source_path_obj.stem
                suffix = source_path_obj.suffix
                new_filename = f"{stem}_{file_hash[:8]}{suffix}"
            else:
                new_filename = source_path_obj.name
        else:
            # Generate a new filename based on hash
            file_hash = AssetManager.get_file_hash(source_path)
            suffix = source_path_obj.suffix
            new_filename = f"{file_hash}{suffix}"

        destination_path = destination_dir_obj / new_filename
        shutil.copy2(source_path, destination_path)

        return str(destination_path)

    @staticmethod
    def organize_assets_by_type(
        source_dir: str,
        destination_base_dir: str,
        create_subdirs: bool = True
    ) -> Dict[str, List[str]]:
        """
        Organize assets into subdirectories by type.

        Args:
            source_dir: Source directory containing assets
            destination_base_dir: Base destination directory
            create_subdirs: Whether to create subdirectories for each type

        Returns:
            Dictionary mapping asset types to lists of moved files
        """
        results = {
            'images': [],
            'documents': [],
            'other': []
        }

        # Find all assets
        all_assets = AssetManager.find_assets_in_directory(
            source_dir,
            list(AssetManager.SUPPORTED_IMAGE_FORMATS | AssetManager.SUPPORTED_DOC_FORMATS)
        )

        for asset_path in all_assets:
            asset_path_obj = Path(asset_path)
            ext = asset_path_obj.suffix.lower()

            if ext in AssetManager.SUPPORTED_IMAGE_FORMATS:
                asset_type = 'images'
            elif ext in AssetManager.SUPPORTED_DOC_FORMATS:
                asset_type = 'documents'
            else:
                asset_type = 'other'

            if create_subdirs:
                dest_dir = Path(destination_base_dir) / asset_type
            else:
                dest_dir = Path(destination_base_dir)

            # Copy asset to destination
            new_path = AssetManager.copy_asset_to_destination(
                asset_path,
                str(dest_dir),
                add_hash=True  # Add hash to avoid conflicts
            )
            results[asset_type].append(new_path)

        return results

    @staticmethod
    def optimize_image(
        source_path: str,
        destination_path: Optional[str] = None,
        quality: int = 85,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        convert_format: Optional[str] = None
    ) -> str:
        """
        Optimize an image by resizing and compressing.

        Args:
            source_path: Path to the source image
            destination_path: Path to save the optimized image (if None, overwrites source)
            quality: JPEG quality percentage (1-100)
            max_width: Maximum width of the image
            max_height: Maximum height of the image
            convert_format: Format to convert to (e.g., 'JPEG', 'PNG', 'WEBP')

        Returns:
            Path to the optimized image
        """
        if destination_path is None:
            destination_path = source_path

        # Open and process the image
        with Image.open(source_path) as img:
            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ('RGBA', 'LA', 'P') and convert_format and convert_format.upper() in ('JPEG', 'JPG'):
                img = img.convert('RGB')
            elif convert_format:
                img = img.convert(convert_format)

            # Calculate new dimensions if resizing is needed
            if max_width or max_height:
                original_width, original_height = img.size
                new_width, new_height = original_width, original_height

                if max_width and original_width > max_width:
                    ratio = max_width / original_width
                    new_width = max_width
                    new_height = int(original_height * ratio)

                if max_height and new_height > max_height:
                    ratio = max_height / new_height
                    new_height = max_height
                    new_width = int(new_width * ratio)

                # Only resize if necessary
                if new_width != original_width or new_height != original_height:
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Determine save parameters
            save_kwargs = {}
            if convert_format:
                format_type = convert_format.upper()
            else:
                format_type = img.format or Path(source_path).suffix[1:].upper()

            # Set quality for formats that support it
            if format_type in ('JPEG', 'JPG'):
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            elif format_type == 'WEBP':
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            elif format_type == 'PNG':
                save_kwargs['optimize'] = True

            # Save the optimized image
            img.save(destination_path, format=format_type, **save_kwargs)

        return destination_path

    @staticmethod
    def batch_optimize_images(
        image_paths: List[str],
        output_dir: Optional[str] = None,
        quality: int = 85,
        max_width: Optional[int] = 1920,
        max_height: Optional[int] = 1080,
        convert_format: Optional[str] = None
    ) -> Dict[str, Dict[str, any]]:
        """
        Optimize multiple images in batch.

        Args:
            image_paths: List of image paths to optimize
            output_dir: Directory to save optimized images (if None, overwrites originals)
            quality: JPEG quality percentage (1-100)
            max_width: Maximum width of images
            max_height: Maximum height of images
            convert_format: Format to convert to (e.g., 'JPEG', 'PNG', 'WEBP')

        Returns:
            Dictionary mapping original paths to optimization results
        """
        results = {}

        for image_path in image_paths:
            try:
                # Prepare output path
                if output_dir:
                    output_path = Path(output_dir) / Path(image_path).name
                    # If converting format, update the extension
                    if convert_format:
                        output_path = output_path.with_suffix(f'.{convert_format.lower()}')
                    output_dir_path = Path(output_dir)
                    output_dir_path.mkdir(parents=True, exist_ok=True)
                else:
                    output_path = image_path

                # Get original file size
                original_size = Path(image_path).stat().st_size

                # Optimize the image
                optimized_path = AssetManager.optimize_image(
                    image_path,
                    str(output_path),
                    quality,
                    max_width,
                    max_height,
                    convert_format
                )

                # Get optimized file size
                optimized_size = Path(optimized_path).stat().st_size

                results[image_path] = {
                    'status': 'success',
                    'optimized_path': optimized_path,
                    'original_size': original_size,
                    'optimized_size': optimized_size,
                    'size_reduced': original_size - optimized_size,
                    'reduction_percentage': round((original_size - optimized_size) / original_size * 100, 2) if original_size > 0 else 0
                }
            except Exception as e:
                results[image_path] = {
                    'status': 'error',
                    'error': str(e)
                }

        return results

    @staticmethod
    def update_markdown_links(
        markdown_content: str,
        old_asset_path: str,
        new_asset_path: str
    ) -> str:
        """
        Update asset links in markdown content.

        Args:
            markdown_content: Original markdown content
            old_asset_path: Old asset path to replace
            new_asset_path: New asset path to use

        Returns:
            Updated markdown content
        """
        # Handle relative paths by normalizing them
        old_path_normalized = os.path.normpath(old_asset_path).replace('\\', '/')
        new_path_normalized = os.path.normpath(new_asset_path).replace('\\', '/')

        # Pattern to match markdown image and link syntax
        # ![alt text](path) or [text](path)
        pattern = r'(!?)\[([^\]]*)\]\(([^)]+)\)'

        def replace_path(match):
            is_image = match.group(1)  # ! for images, empty for links
            text = match.group(2)
            path = match.group(3)

            # Only update if the path matches the old asset path
            # Handle both absolute and relative paths
            if path == old_path_normalized or path.endswith(os.path.basename(old_asset_path)):
                # For relative paths, preserve the relative structure if needed
                # or replace with the new path
                return f"{is_image}[{text}]({new_path_normalized})"

            # Check if the path contains the old asset filename
            if os.path.basename(old_asset_path) in path:
                # Replace the old path with the new path
                new_path = path.replace(os.path.basename(old_asset_path), os.path.basename(new_asset_path))
                return f"{is_image}[{text}]({new_path})"

            # Return original if no match
            return match.group(0)

        updated_content = re.sub(pattern, replace_path, markdown_content)
        return updated_content

    @staticmethod
    def update_markdown_links_batch(
        markdown_content: str,
        asset_mapping: Dict[str, str]
    ) -> str:
        """
        Update multiple asset links in markdown content using a mapping.

        Args:
            markdown_content: Original markdown content
            asset_mapping: Dictionary mapping old paths to new paths

        Returns:
            Updated markdown content
        """
        updated_content = markdown_content

        # Sort asset paths by length in descending order to handle longer paths first
        # This prevents partial replacements when one path is a substring of another
        sorted_mappings = sorted(asset_mapping.items(), key=lambda x: len(x[0]), reverse=True)

        for old_path, new_path in sorted_mappings:
            updated_content = AssetManager.update_markdown_links(
                updated_content,
                old_path,
                new_path
            )

        return updated_content

    @staticmethod
    def extract_all_asset_links(markdown_content: str) -> List[Dict[str, str]]:
        """
        Extract all asset links from markdown content.

        Args:
            markdown_content: Markdown content to scan

        Returns:
            List of dictionaries containing link information
        """
        # Pattern to match markdown image and link syntax
        pattern = r'(!?)\[([^\]]*)\]\(([^)]+)\)'

        links = []
        for match in re.finditer(pattern, markdown_content):
            is_image = match.group(1) == '!'
            text = match.group(2)
            path = match.group(3)

            links.append({
                'type': 'image' if is_image else 'link',
                'text': text,
                'path': path,
                'full_match': match.group(0),
                'start_pos': match.start(),
                'end_pos': match.end()
            })

        return links

    @staticmethod
    def migrate_markdown_assets(
        source_docs_dir: str,
        destination_img_dir: str,
        asset_subdir: str = "img"
    ) -> Dict[str, any]:
        """
        Complete workflow to migrate assets from markdown files to organized structure.

        Args:
            source_docs_dir: Directory containing markdown files with asset links
            destination_img_dir: Base directory for assets (e.g., my-website/static)
            asset_subdir: Subdirectory for images (default: "img")

        Returns:
            Dictionary with migration results
        """
        results = {
            'processed_files': 0,
            'moved_assets': [],
            'updated_files': [],
            'errors': []
        }

        # Find all markdown files
        md_files = AssetManager.find_assets_in_directory(source_docs_dir, ['.md', '.mdx'])

        # Process each markdown file
        for md_file in md_files:
            try:
                # Read the markdown file
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract all asset links
                asset_links = AssetManager.extract_all_asset_links(content)

                # Track asset mappings for this file
                asset_mapping = {}

                for link in asset_links:
                    if link['type'] == 'image':  # Only process image assets for now
                        asset_path = link['path']

                        # If it's a relative path, construct the full path
                        if not asset_path.startswith(('http://', 'https://', '/', 'data:')):
                            # Construct the absolute path to the asset
                            md_dir = Path(md_file).parent
                            full_asset_path = (md_dir / asset_path).resolve()

                            if full_asset_path.exists():
                                # Determine destination path
                                asset_filename = full_asset_path.name
                                dest_asset_path = Path(destination_img_dir) / asset_subdir / asset_filename

                                # Copy asset to destination
                                dest_path_str = AssetManager.copy_asset_to_destination(
                                    str(full_asset_path),
                                    str(Path(destination_img_dir) / asset_subdir),
                                    preserve_filename=True
                                )

                                # Record the mapping
                                asset_mapping[asset_path] = f"/{asset_subdir}/{asset_filename}"
                                results['moved_assets'].append({
                                    'source': str(full_asset_path),
                                    'destination': dest_path_str,
                                    'file': md_file
                                })

                # Update links in the content if we have mappings
                if asset_mapping:
                    updated_content = AssetManager.update_markdown_links_batch(content, asset_mapping)

                    # Write the updated content back to the file
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

                    results['updated_files'].append(md_file)

                results['processed_files'] += 1

            except Exception as e:
                results['errors'].append({
                    'file': md_file,
                    'error': str(e)
                })

        return results

    @staticmethod
    def batch_update_markdown_links(
        markdown_files: List[str],
        asset_mapping: Dict[str, str]
    ) -> Dict[str, bool]:
        """
        Batch update asset links in multiple markdown files.

        Args:
            markdown_files: List of markdown file paths
            asset_mapping: Dictionary mapping old paths to new paths

        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}

        for md_file in markdown_files:
            try:
                # Read the markdown file
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Update links based on the mapping
                updated_content = content
                for old_path, new_path in asset_mapping.items():
                    updated_content = AssetManager.update_markdown_links(
                        updated_content,
                        old_path,
                        new_path
                    )

                # Write the updated content back if it changed
                if updated_content != content:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

                results[md_file] = True
            except Exception as e:
                print(f"Error updating links in {md_file}: {str(e)}")
                results[md_file] = False

        return results

    @staticmethod
    def validate_asset_path(asset_path: str) -> Tuple[bool, str]:
        """
        Validate that an asset path is accessible and valid.

        Args:
            asset_path: Path to the asset

        Returns:
            Tuple of (is_valid, error_message)
        """
        path_obj = Path(asset_path)

        if not path_obj.exists():
            return False, f"Asset does not exist: {asset_path}"

        if not path_obj.is_file():
            return False, f"Path is not a file: {asset_path}"

        # Check if it's a supported format
        ext = path_obj.suffix.lower()
        if ext not in (AssetManager.SUPPORTED_IMAGE_FORMATS | AssetManager.SUPPORTED_DOC_FORMATS):
            return False, f"Unsupported file format: {ext}"

        # For images, try to open and verify it's a valid image
        if ext in AssetManager.SUPPORTED_IMAGE_FORMATS and ext.lower() != '.svg':
            try:
                with Image.open(asset_path) as img:
                    img.verify()
            except Exception as e:
                return False, f"Invalid image file: {str(e)}"

        return True, ""

    @staticmethod
    def validate_assets_integrity(assets_dir: str) -> Dict[str, any]:
        """
        Validate the integrity of all assets in a directory.

        Args:
            assets_dir: Directory containing assets to validate

        Returns:
            Dictionary with validation results
        """
        path_obj = Path(assets_dir)
        if not path_obj.exists():
            return {
                'valid': False,
                'error': f"Directory does not exist: {assets_dir}",
                'assets': []
            }

        results = {
            'valid': True,
            'total_assets': 0,
            'valid_assets': 0,
            'invalid_assets': [],
            'assets': []
        }

        # Find all assets in the directory
        all_assets = AssetManager.find_assets_in_directory(
            assets_dir,
            list(AssetManager.SUPPORTED_IMAGE_FORMATS | AssetManager.SUPPORTED_DOC_FORMATS)
        )

        for asset_path in all_assets:
            is_valid, error_msg = AssetManager.validate_asset_path(asset_path)
            asset_info = AssetManager.get_asset_info(asset_path)

            asset_result = {
                'path': asset_path,
                'valid': is_valid,
                'info': asset_info
            }

            if not is_valid:
                asset_result['error'] = error_msg
                results['invalid_assets'].append(asset_result)
                results['valid'] = False
            else:
                results['valid_assets'] += 1

            results['assets'].append(asset_result)

        results['total_assets'] = len(all_assets)
        results['valid'] = len(results['invalid_assets']) == 0 and results['total_assets'] > 0

        return results

    @staticmethod
    def check_broken_links_in_markdown(
        markdown_files: List[str],
        assets_base_dir: str
    ) -> Dict[str, any]:
        """
        Check for broken asset links in markdown files.

        Args:
            markdown_files: List of markdown file paths to check
            assets_base_dir: Base directory where assets should be located

        Returns:
            Dictionary with broken link information
        """
        results = {
            'total_files': len(markdown_files),
            'files_checked': 0,
            'broken_links': [],
            'valid_links': 0
        }

        for md_file in markdown_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                asset_links = AssetManager.extract_all_asset_links(content)

                for link in asset_links:
                    path = link['path']

                    # Only check local asset paths, not external URLs
                    if not path.startswith(('http://', 'https://', 'data:')):
                        # If it's an absolute path starting with /, join with assets base dir
                        if path.startswith('/'):
                            full_path = Path(assets_base_dir) / path[1:]  # Remove leading slash
                        else:
                            # It's a relative path, construct relative to the markdown file
                            md_dir = Path(md_file).parent
                            full_path = (md_dir / path).resolve()

                        # Check if the asset exists
                        if not full_path.exists():
                            results['broken_links'].append({
                                'file': md_file,
                                'link': path,
                                'resolved_path': str(full_path),
                                'link_text': link['text'],
                                'type': link['type']
                            })
                        else:
                            results['valid_links'] += 1

                results['files_checked'] += 1

            except Exception as e:
                results['broken_links'].append({
                    'file': md_file,
                    'error': str(e)
                })

        return results

    @staticmethod
    def generate_asset_report(assets_dir: str) -> Dict[str, any]:
        """
        Generate a comprehensive report about assets in a directory.

        Args:
            assets_dir: Directory containing assets

        Returns:
            Dictionary with asset report
        """
        validation_results = AssetManager.validate_assets_integrity(assets_dir)

        report = {
            'directory': assets_dir,
            'validation': validation_results,
            'statistics': {},
            'recommendations': []
        }

        # Generate statistics
        if validation_results['assets']:
            total_size = sum(asset['info']['size_bytes'] for asset in validation_results['assets'])
            image_count = sum(1 for asset in validation_results['assets'] if asset['info']['is_image'])
            doc_count = sum(1 for asset in validation_results['assets'] if asset['info']['is_document'])

            report['statistics'] = {
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_assets': validation_results['total_assets'],
                'image_count': image_count,
                'document_count': doc_count,
                'average_size_bytes': total_size // validation_results['total_assets'] if validation_results['total_assets'] > 0 else 0
            }

            # Generate recommendations based on the validation
            if validation_results['invalid_assets']:
                report['recommendations'].append(
                    f"Fix {len(validation_results['invalid_assets'])} invalid assets"
                )

            large_assets = [
                asset for asset in validation_results['assets']
                if asset['info']['size_bytes'] > 1024 * 1024  # Larger than 1MB
            ]
            if large_assets:
                report['recommendations'].append(
                    f"Consider optimizing {len(large_assets)} large assets (>1MB)"
                )

        return report

    @staticmethod
    def get_asset_info(asset_path: str) -> Dict[str, any]:
        """
        Get information about an asset.

        Args:
            asset_path: Path to the asset

        Returns:
            Dictionary with asset information
        """
        path_obj = Path(asset_path)

        info = {
            'path': str(path_obj),
            'name': path_obj.name,
            'extension': path_obj.suffix.lower(),
            'size_bytes': path_obj.stat().st_size,
            'size_mb': round(path_obj.stat().st_size / (1024 * 1024), 2),
            'modified': path_obj.stat().st_mtime,
            'is_image': path_obj.suffix.lower() in AssetManager.SUPPORTED_IMAGE_FORMATS,
            'is_document': path_obj.suffix.lower() in AssetManager.SUPPORTED_DOC_FORMATS,
        }

        # Add image-specific information if it's an image
        if info['is_image'] and path_obj.suffix.lower() != '.svg':
            try:
                with Image.open(asset_path) as img:
                    width, height = img.size
                    info['width'] = width
                    info['height'] = height
                    info['aspect_ratio'] = round(width / height, 2) if height > 0 else 0
                    info['mode'] = img.mode
            except Exception:
                # If we can't read the image info, just continue
                pass

        return info

    @staticmethod
    def cleanup_duplicate_assets(asset_dir: str) -> List[str]:
        """
        Find and remove duplicate assets in a directory.

        Args:
            asset_dir: Directory to check for duplicates

        Returns:
            List of removed duplicate file paths
        """
        path_obj = Path(asset_dir)
        if not path_obj.exists():
            return []

        # Group files by size first (optimization)
        files_by_size = {}
        for file_path in path_obj.rglob('*'):
            if file_path.is_file():
                size = file_path.stat().st_size
                if size not in files_by_size:
                    files_by_size[size] = []
                files_by_size[size].append(file_path)

        # Find duplicates by comparing hashes
        removed_files = []
        for size, files in files_by_size.items():
            if len(files) > 1:  # Only process if there are multiple files of the same size
                hashes = {}
                for file_path in files:
                    file_hash = AssetManager.get_file_hash(str(file_path))
                    if file_hash in hashes:
                        # Duplicate found, remove the current file
                        file_path.unlink()
                        removed_files.append(str(file_path))
                        print(f"Removed duplicate: {file_path}")
                    else:
                        hashes[file_hash] = str(file_path)

        return removed_files