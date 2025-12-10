# Alembic Database Migrations

This directory contains the configuration for database migrations using Alembic.

## Setup

To initialize the database with the current models:

```bash
cd backend
python init_db.py
```

## Creating New Migrations

To create a new migration after making changes to models:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

## Applying Migrations

To apply pending migrations:

```bash
cd backend
alembic upgrade head
```

## Rolling Back Migrations

To roll back to a previous migration:

```bash
cd backend
alembic downgrade -1  # Go back one migration
# or
alembic downgrade <revision_id>  # Go back to specific migration
```

## Checking Migration Status

To check the current migration status:

```bash
cd backend
alembic current
```

## Configuration

- `alembic.ini`: Main configuration file
- `env.py`: Environment configuration that connects to the database using settings
- `script.py.mako`: Template for generating migration files
- `versions/`: Directory containing migration files (created automatically)

## Models

The following models are tracked by Alembic:
- User
- UserPreferences
- Textbook
- Chapter
- Section

All models are imported in `env.py` to ensure they are included in autogenerate operations.