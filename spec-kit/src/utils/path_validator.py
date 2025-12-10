import os
from pathlib import Path
from typing import Dict, List, Optional


def validate_path_exists(path: str) -> bool:
    """
    Check if a path exists on the filesystem.

    Args:
        path: Path to validate

    Returns:
        True if path exists, False otherwise
    """
    try:
        return Path(path).exists()
    except Exception:
        return False


def validate_paths_structure(paths: Dict[str, str]) -> Dict[str, bool]:
    """
    Validate multiple paths and return a dictionary indicating which exist.

    Args:
        paths: Dictionary mapping path names to their paths

    Returns:
        Dictionary mapping path names to boolean indicating existence
    """
    result = {}
    for name, path in paths.items():
        result[name] = validate_path_exists(path)
    return result


def validate_path_is_directory(path: str) -> bool:
    """
    Check if a path exists and is a directory.

    Args:
        path: Path to validate

    Returns:
        True if path exists and is a directory, False otherwise
    """
    try:
        return Path(path).is_dir()
    except Exception:
        return False


def validate_path_is_file(path: str) -> bool:
    """
    Check if a path exists and is a file.

    Args:
        path: Path to validate

    Returns:
        True if path exists and is a file, False otherwise
    """
    try:
        return Path(path).is_file()
    except Exception:
        return False


def validate_project_structure(
    constitution_path: str,
    history_path: str,
    spec_folder: str,
    docs_folder: str,
    assets_folder: str
) -> Dict[str, bool]:
    """
    Validate the complete project structure for the SDD framework.

    Args:
        constitution_path: Path to constitution file
        history_path: Path to history prompts directory
        spec_folder: Path to spec folder
        docs_folder: Path to docs folder
        assets_folder: Path to assets folder

    Returns:
        Dictionary indicating which paths exist
    """
    paths_to_check = {
        "constitution": constitution_path,
        "history": history_path,
        "spec": spec_folder,
        "docs": docs_folder,
        "assets": assets_folder
    }

    return validate_paths_structure(paths_to_check)