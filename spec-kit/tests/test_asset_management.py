import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from src.utils.asset_manager import AssetManager


def create_test_image(path, size=(100, 100), color=(255, 0, 0)):
    """Create a test image file."""
    img = Image.new('RGB', size, color)
    img.save(path, 'PNG')
    return path


def test_get_file_hash():
    """Test generating file hash."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Hello, World!")

        hash1 = AssetManager.get_file_hash(str(test_file))
        hash2 = AssetManager.get_file_hash(str(test_file))

        # Same file should have same hash
        assert hash1 == hash2

        # Different content should have different hashes
        test_file2 = Path(temp_dir) / "test2.txt"
        test_file2.write_text("Hello, World!!")
        hash3 = AssetManager.get_file_hash(str(test_file2))

        assert hash1 != hash3


def test_find_assets_in_directory():
    """Test finding assets in a directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        (Path(temp_dir) / "image1.jpg").touch()
        (Path(temp_dir) / "image2.png").touch()
        (Path(temp_dir) / "doc1.pdf").touch()
        (Path(temp_dir) / "not_an_asset.txt").touch()

        # Find image assets
        image_assets = AssetManager.find_assets_in_directory(
            temp_dir,
            ['.jpg', '.png']
        )
        assert len(image_assets) == 2
        assert any("image1.jpg" in path for path in image_assets)
        assert any("image2.png" in path for path in image_assets)

        # Find all supported assets
        all_assets = AssetManager.find_assets_in_directory(temp_dir)
        # Should find image files and PDF, but not txt
        assert len(all_assets) >= 3  # At least the 2 images and 1 PDF


def test_copy_asset_to_destination():
    """Test copying an asset to destination."""
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / "source"
        dest_dir = Path(temp_dir) / "destination"
        source_dir.mkdir()
        dest_dir.mkdir()

        source_file = source_dir / "test.jpg"
        source_file.write_text("test content")

        # Copy asset
        copied_path = AssetManager.copy_asset_to_destination(
            str(source_file),
            str(dest_dir)
        )

        assert Path(copied_path).exists()
        assert Path(copied_path).name == "test.jpg"
        assert (dest_dir / "test.jpg").exists()


def test_organize_assets_by_type():
    """Test organizing assets by type."""
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / "source"
        dest_dir = Path(temp_dir) / "destination"
        source_dir.mkdir()

        # Create test files
        create_test_image(source_dir / "img1.jpg", (100, 100), (255, 0, 0))
        create_test_image(source_dir / "img2.png", (200, 200), (0, 255, 0))
        (source_dir / "doc1.pdf").write_text("PDF content")
        (source_dir / "doc2.txt").write_text("Text content")

        # Organize assets
        results = AssetManager.organize_assets_by_type(
            str(source_dir),
            str(dest_dir)
        )

        # Check results structure
        assert 'images' in results
        assert 'documents' in results
        assert 'other' in results

        # Check that files were organized properly
        images_dir = dest_dir / "images"
        docs_dir = dest_dir / "documents"
        other_dir = dest_dir / "other"

        assert images_dir.exists()
        assert docs_dir.exists()
        # 'other' might not exist if no other files were found

        # Check that image files were moved to images directory
        image_files = list(images_dir.glob("*"))
        assert len(image_files) >= 2  # The 2 images we created

        # Check that document files were moved to documents directory
        doc_files = list(docs_dir.glob("*"))
        assert len(doc_files) >= 2  # The PDF and TXT we created


def test_update_markdown_links():
    """Test updating markdown links."""
    original_content = """# Test Document

Here is an image: ![Alt text](old/path/image.jpg)

And a link: [Link text](old/path/doc.pdf)

![Another image](assets/photo.png)
"""

    updated_content = AssetManager.update_markdown_links(
        original_content,
        "old/path/image.jpg",
        "/img/new_image.jpg"
    )

    assert "/img/new_image.jpg" in updated_content
    assert "old/path/image.jpg" not in updated_content


def test_extract_all_asset_links():
    """Test extracting all asset links from markdown."""
    markdown_content = """# Test Document

Here is an image: ![Alt text](path/image.jpg)

And a link: [Link text](path/doc.pdf)

![Another image](/assets/photo.png)

[External link](https://example.com/image.jpg)
"""

    links = AssetManager.extract_all_asset_links(markdown_content)

    assert len(links) == 4  # 2 images + 2 links
    image_links = [link for link in links if link['type'] == 'image']
    assert len(image_links) == 2
    link_links = [link for link in links if link['type'] == 'link']
    assert len(link_links) == 2


def test_optimize_image():
    """Test image optimization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test image
        source_img = Path(temp_dir) / "source.png"
        create_test_image(source_img, (500, 500), (100, 150, 200))

        # Optimize the image
        dest_img = Path(temp_dir) / "optimized.jpg"
        optimized_path = AssetManager.optimize_image(
            str(source_img),
            str(dest_img),
            quality=50,
            max_width=200,
            max_height=200
        )

        assert Path(optimized_path).exists()

        # Verify the optimized image has the expected properties
        with Image.open(optimized_path) as img:
            width, height = img.size
            assert width <= 200
            assert height <= 200


def test_batch_optimize_images():
    """Test batch image optimization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "optimized"
        output_dir.mkdir()

        # Create test images
        img1 = Path(temp_dir) / "img1.png"
        img2 = Path(temp_dir) / "img2.jpg"
        create_test_image(img1, (400, 400), (255, 0, 0))
        create_test_image(img2, (300, 300), (0, 255, 0))

        image_paths = [str(img1), str(img2)]

        # Batch optimize
        results = AssetManager.batch_optimize_images(
            image_paths,
            str(output_dir),
            quality=75,
            max_width=250,
            max_height=250
        )

        assert len(results) == 2
        for original_path, result in results.items():
            assert result['status'] == 'success'
            assert Path(result['optimized_path']).exists()

            # Check that the image was actually resized
            with Image.open(result['optimized_path']) as img:
                width, height = img.size
                assert width <= 250
                assert height <= 250


def test_validate_asset_path():
    """Test asset path validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a valid image
        valid_img = Path(temp_dir) / "valid.png"
        create_test_image(valid_img)

        # Create an invalid image (text file with image extension)
        invalid_img = Path(temp_dir) / "invalid.png"
        invalid_img.write_text("not an image")

        # Test valid image
        is_valid, error = AssetManager.validate_asset_path(str(valid_img))
        assert is_valid is True
        assert error == ""

        # Test invalid image
        is_valid, error = AssetManager.validate_asset_path(str(invalid_img))
        assert is_valid is False
        assert "Invalid image file" in error

        # Test non-existent file
        is_valid, error = AssetManager.validate_asset_path(str(Path(temp_dir) / "nonexistent.jpg"))
        assert is_valid is False
        assert "does not exist" in error


def test_validate_assets_integrity():
    """Test validating assets integrity in a directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test assets
        valid_img = Path(temp_dir) / "valid.png"
        create_test_image(valid_img)

        invalid_file = Path(temp_dir) / "invalid.png"
        invalid_file.write_text("not an image")

        # Validate integrity
        results = AssetManager.validate_assets_integrity(temp_dir)

        assert results['total_assets'] == 2
        assert results['valid_assets'] == 1  # Only the valid image
        assert len(results['invalid_assets']) == 1


def test_check_broken_links_in_markdown():
    """Test checking for broken links in markdown files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a markdown file with both valid and invalid links
        md_file = Path(temp_dir) / "test.md"
        valid_img = Path(temp_dir) / "valid.png"
        create_test_image(valid_img)

        md_content = f"""# Test

![Valid Image](valid.png)
![Invalid Image](missing.jpg)
![Another Valid](./valid.png)
"""
        md_file.write_text(md_content)

        # Check for broken links
        results = AssetManager.check_broken_links_in_markdown(
            [str(md_file)],
            temp_dir
        )

        # Should find 1 broken link (missing.jpg)
        assert len(results['broken_links']) == 1
        assert results['broken_links'][0]['link'] == 'missing.jpg'


def test_get_asset_info():
    """Test getting asset information."""
    with tempfile.TemporaryDirectory() as temp_dir:
        img_path = Path(temp_dir) / "test.png"
        create_test_image(img_path, (300, 200))

        info = AssetManager.get_asset_info(str(img_path))

        assert info['name'] == 'test.png'
        assert info['extension'] == '.png'
        assert info['is_image'] is True
        assert info['is_document'] is False
        assert info['width'] == 300
        assert info['height'] == 200
        assert info['aspect_ratio'] == 1.5