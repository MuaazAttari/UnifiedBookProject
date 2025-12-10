# OpenAI Integration

This document explains how the Textbook Generation application integrates with OpenAI's API for content generation.

## Overview

The application uses OpenAI's GPT models to generate educational content for textbooks. The integration includes:

1. **Content Generation Service** - Core service for generating textbook content
2. **Textbook Generation Service** - Orchestrates the full textbook creation process
3. **Formatting Service** - Handles export to different formats (PDF, DOCX, HTML)

## Services

### ContentGenerationService

Located in `src/services/content_generation.py`, this service provides:

- `generate_textbook_outline()` - Creates a structured outline for a textbook
- `generate_chapter_content()` - Generates detailed content for a chapter
- `generate_section_content()` - Creates content for specific sections
- `improve_content()` - Enhances existing content based on feedback

### TextbookGenerationService

Located in `src/services/textbook_generation.py`, this service:

- Orchestrates the textbook creation process
- Integrates with the database to store generated content
- Manages the generation workflow from outline to complete textbook

### FormattingService

Located in `src/services/formatting.py`, this service:

- Exports textbooks to various formats (PDF, DOCX, HTML)
- Uses WeasyPrint for PDF generation
- Uses python-docx for DOCX generation

## API Endpoints

The OpenAI integration is exposed through the following API endpoints:

- `POST /api/v1/textbook/generate` - Generate a new textbook
- `GET /api/v1/textbook/{id}` - Get textbook status and content
- `PUT /api/v1/chapter/{id}` - Update chapter content
- `POST /api/v1/improve-content/{id}` - Improve content with AI based on feedback
- `POST /api/v1/textbook/{id}/export` - Export textbook in specified format

## Configuration

The OpenAI integration is configured through environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key (required)

## Usage Examples

### Generating a Textbook

```python
from src.services.textbook_generation import textbook_generation_service

textbook = await textbook_generation_service.generate_textbook(
    db=session,
    subject="Introduction to Computer Science",
    title="CS101 Textbook",
    educational_level="UNDERGRADUATE",
    user_id="user-123",
    settings={"chapters_count": 10}
)
```

### Improving Content with Feedback

```python
from src.services.textbook_generation import textbook_generation_service

improved_content = await textbook_generation_service.update_content_with_feedback(
    db=session,
    content_id="chapter-123",
    content_type="chapter",  # or "section"
    feedback="Make this explanation clearer for beginners",
    educational_level="UNDERGRADUATE"
)
```

## Security Considerations

- API keys are stored in environment variables, not in code
- Rate limiting should be implemented based on your OpenAI plan
- Content generation should be monitored for quality and appropriateness
- User-generated prompts should be validated and sanitized

## Error Handling

The service includes error handling for:

- API connection issues
- Rate limiting
- Invalid requests
- Content generation failures

In case of errors, the system falls back to appropriate default responses.

## Educational Level Support

The system supports different educational levels:
- K12
- UNDERGRADUATE
- GRADUATE

Content is tailored to the appropriate level of complexity and detail.