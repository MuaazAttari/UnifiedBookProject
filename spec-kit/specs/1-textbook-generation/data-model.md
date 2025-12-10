# Data Model: Textbook Generation

## Entities

### Textbook
- **id**: string (UUID) - Unique identifier for the textbook
- **title**: string - Title of the textbook
- **subject**: string - Subject area or topic of the textbook
- **educational_level**: enum (K12, UNDERGRADUATE, GRADUATE) - Target educational level
- **created_at**: datetime - Timestamp of creation
- **updated_at**: datetime - Timestamp of last update
- **status**: enum (DRAFT, GENERATING, COMPLETED, REVIEWED) - Current status of the textbook
- **user_id**: string (UUID) - Reference to the user who created the textbook
- **settings**: JSON object - Formatting and generation preferences
- **relationships**:
  - Has many → Chapters
  - Belongs to → User

### Chapter
- **id**: string (UUID) - Unique identifier for the chapter
- **title**: string - Title of the chapter
- **content**: text - Main content of the chapter
- **position**: integer - Order of the chapter in the textbook
- **textbook_id**: string (UUID) - Reference to the parent textbook
- **created_at**: datetime - Timestamp of creation
- **updated_at**: datetime - Timestamp of last update
- **status**: enum (DRAFT, GENERATING, COMPLETED, REVIEWED) - Current status
- **relationships**:
  - Belongs to → Textbook
  - Has many → Sections

### Section
- **id**: string (UUID) - Unique identifier for the section
- **title**: string - Title of the section
- **content**: text - Content of the section
- **position**: integer - Order of the section in the chapter
- **chapter_id**: string (UUID) - Reference to the parent chapter
- **created_at**: datetime - Timestamp of creation
- **updated_at**: datetime - Timestamp of last update
- **type**: enum (CONTENT, SUMMARY, EXERCISE, KEY_POINT) - Type of section content
- **relationships**:
  - Belongs to → Chapter

### User
- **id**: string (UUID) - Unique identifier for the user
- **name**: string - User's name
- **email**: string - User's email address
- **created_at**: datetime - Account creation timestamp
- **updated_at**: datetime - Timestamp of last update
- **preferences**: JSON object - User preferences for textbook generation
- **relationships**:
  - Has many → Textbooks

### UserPreferences
- **id**: string (UUID) - Unique identifier
- **user_id**: string (UUID) - Reference to the user
- **default_educational_level**: enum (K12, UNDERGRADUATE, GRADUATE) - Default level for generation
- **default_format**: string - Default output format (PDF, DOCX, etc.)
- **default_style**: string - Default styling preferences
- **created_at**: datetime - Timestamp of creation
- **updated_at**: datetime - Timestamp of last update
- **relationships**:
  - Belongs to → User

## Validation Rules

### Textbook
- Title must be between 5 and 200 characters
- Subject must be provided and not empty
- Educational level must be one of the defined enum values
- Status must be one of the defined enum values

### Chapter
- Title must be between 3 and 100 characters
- Content must be provided when status is COMPLETED or REVIEWED
- Position must be a positive integer
- Must belong to a valid textbook

### Section
- Title must be between 3 and 100 characters (if provided)
- Content must be provided when status is COMPLETED or REVIEWED
- Position must be a positive integer
- Type must be one of the defined enum values
- Must belong to a valid chapter

### User
- Email must be valid and unique
- Name must be provided

### UserPreferences
- Must have a valid user reference
- Default educational level must be one of the enum values

## State Transitions

### Textbook
- DRAFT → GENERATING (when generation is initiated)
- GENERATING → COMPLETED (when generation is finished)
- COMPLETED → REVIEWED (when user completes review)

### Chapter
- DRAFT → GENERATING (when chapter generation is initiated)
- GENERATING → COMPLETED (when generation is finished)
- COMPLETED → REVIEWED (when user reviews and approves)

### Section
- DRAFT → GENERATING (when section generation is initiated)
- GENERATING → COMPLETED (when generation is finished)
- COMPLETED → REVIEWED (when user reviews and approves)