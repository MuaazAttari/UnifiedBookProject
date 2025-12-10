# Data Model: Unified Textbook Generation and RAG System

**Created**: 2025-12-10
**Feature**: 2-memorize-config (Textbook Generation & RAG System)

## Overview

This document defines the data models for the Unified Physical AI & Humanoid Robotics Learning Book project. It includes entities for textbook content, user management, chat interactions, and system configuration.

## Entity Models

### 1. Configuration

**Purpose**: Stores system configuration paths and settings

**Fields**:
- config_id: string (primary key, unique identifier)
- constitution_path: string (path to constitution file, e.g., ".specify/memory/constitution.md")
- history_path: string (path to history prompts, e.g., "history/prompts/")
- spec_folder: string (path to spec folder, e.g., project root)
- docs_folder: string (path to docs folder, e.g., "../my-website/docs/")
- assets_folder: string (path to assets folder, e.g., "../my-website/static/")
- root_folder: string (path to root folder, e.g., "../")
- created_at: datetime (timestamp when configuration was created)
- updated_at: datetime (timestamp when configuration was last updated)

**Relationships**:
- One-to-many with Chapters (via docs_folder reference)

### 2. Chapter

**Purpose**: Represents a chapter in the textbook

**Fields**:
- chapter_id: string (primary key, unique identifier)
- title: string (chapter title)
- content: string (markdown content of the chapter)
- frontmatter: json (frontmatter data including id, title, sidebar_label)
- order: integer (sequence order of the chapter in the book)
- path: string (relative path in docs folder)
- slug: string (URL-friendly version of the title)
- description: string (brief description of the chapter content)
- created_at: datetime (timestamp when chapter was created)
- updated_at: datetime (timestamp when chapter was last updated)

**Validation Rules**:
- title must not be empty
- order must be unique within a book context
- frontmatter must contain required fields (id, title, sidebar_label)

### 3. User

**Purpose**: Represents a registered user of the system

**Fields**:
- user_id: string (primary key, unique identifier)
- name: string (user's full name)
- email: string (user's email address, must be unique)
- password_hash: string (hashed password for authentication)
- software_experience: string (level: beginner, intermediate, expert)
- hardware_availability: string (description of available hardware)
- robotics_familiarity: string (level: beginner, intermediate, expert)
- created_at: datetime (timestamp when user registered)
- updated_at: datetime (timestamp when user profile was last updated)
- last_login_at: datetime (timestamp of last login)
- is_active: boolean (whether the account is active)

**Validation Rules**:
- email must be valid and unique
- password must meet security requirements
- experience levels must be from predefined set

### 4. ChatSession

**Purpose**: Represents a chat session between user and RAG system

**Fields**:
- session_id: string (primary key, unique identifier)
- user_id: string (foreign key referencing User)
- query: string (user's question/query)
- response: string (AI's response to the query)
- context_type: string (enum: "full_book", "selected_text")
- selected_text: string (text selected for context, if applicable)
- query_timestamp: datetime (when the query was made)
- response_timestamp: datetime (when the response was generated)
- tokens_used: integer (number of tokens in the interaction)
- is_active: boolean (whether session is currently active)

**Validation Rules**:
- user_id must reference an existing user
- context_type must be from predefined set
- query and response must not exceed size limits

### 5. TranslationCache

**Purpose**: Caches translations to improve performance

**Fields**:
- cache_id: string (primary key, unique identifier)
- original_text: string (text in original language)
- translated_text: string (text in target language)
- source_language: string (language code of original text)
- target_language: string (language code of translated text)
- created_at: datetime (timestamp when translation was cached)
- expires_at: datetime (timestamp when cache entry expires)

**Validation Rules**:
- original_text and translated_text must not be empty
- language codes must be valid ISO codes

### 6. PersonalizationProfile

**Purpose**: Stores personalization preferences for each user per chapter

**Fields**:
- profile_id: string (primary key, unique identifier)
- user_id: string (foreign key referencing User)
- chapter_id: string (foreign key referencing Chapter)
- difficulty_level: string (personalized difficulty: beginner, intermediate, expert)
- content_preferences: json (user's content preferences)
- personalization_enabled: boolean (whether personalization is active)
- created_at: datetime (timestamp when profile was created)
- updated_at: datetime (timestamp when profile was last updated)

**Validation Rules**:
- user_id must reference an existing user
- chapter_id must reference an existing chapter
- difficulty_level must be from predefined set

## Relationships

### Chapter and ChatSession
- One Chapter can be referenced in multiple ChatSessions (when using "selected_text" context)
- Foreign key: chat_session.chapter_id references chapter.chapter_id

### User and ChatSession
- One User can have multiple ChatSessions
- Foreign key: chat_session.user_id references user.user_id

### User and PersonalizationProfile
- One User can have multiple PersonalizationProfiles (one per chapter)
- Foreign key: personalization_profile.user_id references user.user_id

### Chapter and PersonalizationProfile
- One Chapter can have multiple PersonalizationProfiles (one per user)
- Foreign key: personalization_profile.chapter_id references chapter.chapter_id

## Indexes

### Configuration
- Index on config_id (primary)

### Chapter
- Index on order (for sorting)
- Index on slug (for URL routing)
- Index on path (for file system operations)

### User
- Index on email (for authentication)
- Index on user_id (primary)

### ChatSession
- Index on user_id (for user-specific queries)
- Index on query_timestamp (for chronological sorting)
- Index on context_type (for filtering by context)

### TranslationCache
- Index on original_text (for cache lookup)
- Index on source_language and target_language (for language-specific queries)

### PersonalizationProfile
- Index on user_id and chapter_id (for unique user-chapter combinations)
- Index on difficulty_level (for filtering by preference)

## Constraints

### Referential Integrity
- ChatSession.user_id must reference an existing User
- ChatSession.chapter_id must reference an existing Chapter (when context_type is "selected_text")
- PersonalizationProfile.user_id must reference an existing User
- PersonalizationProfile.chapter_id must reference an existing Chapter

### Uniqueness
- User.email must be unique
- PersonalizationProfile.user_id and PersonalizationProfile.chapter_id combination must be unique

### Data Validation
- All timestamp fields must be in valid datetime format
- Text fields must meet minimum and maximum length requirements
- Enum fields must contain values from predefined sets