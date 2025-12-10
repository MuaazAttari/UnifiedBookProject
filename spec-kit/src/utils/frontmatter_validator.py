from typing import Dict, List, Tuple


def validate_frontmatter(frontmatter: Dict) -> Tuple[bool, List[str]]:
    """
    Validate the structure and content of frontmatter.

    Args:
        frontmatter: Dictionary containing frontmatter data

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check for required fields
    required_fields = ['id', 'title', 'sidebar_label']
    for field in required_fields:
        if field not in frontmatter or not frontmatter[field]:
            errors.append(f"Missing required field: {field}")

    # Validate field types and formats
    if 'id' in frontmatter:
        if not isinstance(frontmatter['id'], str) or not frontmatter['id'].strip():
            errors.append("Field 'id' must be a non-empty string")
        elif not frontmatter['id'].replace('_', '').replace('-', '').isalnum():
            errors.append("Field 'id' should contain only alphanumeric characters, hyphens, and underscores")

    if 'title' in frontmatter:
        if not isinstance(frontmatter['title'], str) or not frontmatter['title'].strip():
            errors.append("Field 'title' must be a non-empty string")

    if 'sidebar_label' in frontmatter:
        if not isinstance(frontmatter['sidebar_label'], str) or not frontmatter['sidebar_label'].strip():
            errors.append("Field 'sidebar_label' must be a non-empty string")

    if 'order' in frontmatter:
        if not isinstance(frontmatter['order'], int):
            errors.append("Field 'order' must be an integer")

    if 'description' in frontmatter:
        if not isinstance(frontmatter['description'], str):
            errors.append("Field 'description' must be a string")

    # Check for valid slug format if present
    if 'slug' in frontmatter:
        if not isinstance(frontmatter['slug'], str) or not frontmatter['slug'].strip():
            errors.append("Field 'slug' must be a non-empty string")
        elif not frontmatter['slug'].replace('_', '').replace('-', '').replace('/', '').isalnum():
            errors.append("Field 'slug' should contain only alphanumeric characters, hyphens, underscores, and forward slashes")

    return len(errors) == 0, errors


def normalize_frontmatter(frontmatter: Dict) -> Dict:
    """
    Normalize frontmatter by ensuring consistent formatting.

    Args:
        frontmatter: Dictionary containing frontmatter data

    Returns:
        Normalized frontmatter dictionary
    """
    normalized = frontmatter.copy()

    # Ensure required fields exist with defaults if missing
    if 'id' not in normalized:
        normalized['id'] = ''
    if 'title' not in normalized:
        normalized['title'] = ''
    if 'sidebar_label' not in normalized:
        normalized['sidebar_label'] = normalized.get('title', '')

    # Ensure order is an integer
    if 'order' in normalized:
        try:
            normalized['order'] = int(normalized['order'])
        except (ValueError, TypeError):
            normalized['order'] = 0

    # Ensure description is a string
    if 'description' in normalized:
        normalized['description'] = str(normalized['description'])

    return normalized


def validate_frontmatter_compliance(frontmatter: Dict) -> Tuple[bool, List[str]]:
    """
    Validate frontmatter specifically for Docusaurus compliance.

    Args:
        frontmatter: Dictionary containing frontmatter data

    Returns:
        Tuple of (is_valid, list_of_docusaurus_specific_errors)
    """
    errors = []

    # Docusaurus specific validations
    if 'id' in frontmatter:
        # Docusaurus IDs should not contain special characters that might cause issues
        id_val = frontmatter['id']
        if not id_val.replace('_', '').replace('-', '').replace('/', '').isalnum():
            errors.append(f"Docusaurus ID '{id_val}' should only contain alphanumeric characters, hyphens, underscores, and forward slashes")

    # Validate draft status if present
    if 'draft' in frontmatter:
        if not isinstance(frontmatter['draft'], bool):
            errors.append("Field 'draft' must be a boolean value")

    # Validate custom edit URL if present
    if 'custom_edit_url' in frontmatter:
        if not isinstance(frontmatter['custom_edit_url'], str):
            errors.append("Field 'custom_edit_url' must be a string")

    # Validate image paths if present
    if 'image' in frontmatter:
        if not isinstance(frontmatter['image'], str):
            errors.append("Field 'image' must be a string path")

    # Validate tags if present
    if 'tags' in frontmatter:
        if not isinstance(frontmatter['tags'], list):
            errors.append("Field 'tags' must be a list")
        else:
            for i, tag in enumerate(frontmatter['tags']):
                if not isinstance(tag, str):
                    errors.append(f"Tag at index {i} must be a string")

    return len(errors) == 0, errors


def verify_frontmatter_compliance(frontmatter: Dict, strict: bool = False) -> Dict[str, any]:
    """
    Comprehensive frontmatter compliance verification with detailed reporting.

    Args:
        frontmatter: Dictionary containing frontmatter data
        strict: Whether to enforce stricter validation rules

    Returns:
        Dictionary with compliance details
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': [],
        'compliant': True
    }

    # Run basic validation
    is_valid, errors = validate_frontmatter(frontmatter)
    result['errors'].extend(errors)

    # Run Docusaurus compliance validation
    is_compliant, compliance_errors = validate_frontmatter_compliance(frontmatter)
    result['errors'].extend(compliance_errors)

    # Check for recommended fields
    recommended_fields = ['description', 'image']
    missing_recommended = [field for field in recommended_fields if field not in frontmatter]
    if missing_recommended:
        result['warnings'].append(f"Missing recommended fields: {', '.join(missing_recommended)}")

    # Additional checks for strict mode
    if strict:
        # Check for SEO-related fields
        seo_fields = ['title', 'description']
        for field in seo_fields:
            if field in frontmatter:
                value = frontmatter[field]
                if isinstance(value, str):
                    if field == 'title' and len(value) > 60:
                        result['warnings'].append(f"Title is quite long ({len(value)} chars), consider keeping it under 60 chars for SEO")
                    elif field == 'description' and (len(value) < 50 or len(value) > 160):
                        result['warnings'].append(f"Description should be between 50-160 characters for optimal SEO (currently {len(value)} chars)")

    # Determine overall status
    result['valid'] = len(result['errors']) == 0
    result['compliant'] = result['valid']  # For this context, valid means compliant

    if result['valid'] and result['warnings']:
        # Has warnings but no errors - partially compliant
        result['compliant'] = False

    return result