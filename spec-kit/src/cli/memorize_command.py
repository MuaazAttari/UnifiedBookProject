import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.db.database import get_db
from src.services.configuration_service import ConfigurationService
from src.utils.path_validator import validate_project_structure


def memorize_paths():
    """
    CLI command to memorize project configuration paths.
    """
    parser = argparse.ArgumentParser(description="Memorize project configuration paths")
    parser.add_argument("--constitution", required=True, help="Path to constitution file")
    parser.add_argument("--history", required=True, help="Path to history prompts directory")
    parser.add_argument("--spec-folder", required=True, help="Path to spec folder")
    parser.add_argument("--docs-folder", required=True, help="Path to docs folder")
    parser.add_argument("--assets-folder", required=True, help="Path to assets folder")
    parser.add_argument("--root-folder", required=True, help="Path to root folder")
    parser.add_argument("--db-url", help="Database URL (overrides config)")

    args = parser.parse_args()

    # Validate paths exist
    validation_result = validate_project_structure(
        constitution_path=args.constitution,
        history_path=args.history,
        spec_folder=args.spec_folder,
        docs_folder=args.docs_folder,
        assets_folder=args.assets_folder
    )

    invalid_paths = [path for path, exists in validation_result.items() if not exists]
    if invalid_paths:
        print(f"Error: The following paths do not exist: {', '.join(invalid_paths)}")
        sys.exit(1)

    # Connect to database
    db_url = args.db_url or str(settings.DATABASE_URL)
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if configuration already exists for this docs folder
        existing_config = ConfigurationService.get_configuration_by_path(db, args.docs_folder)
        if existing_config:
            print(f"Configuration already exists for docs folder: {args.docs_folder}")
            response = input("Do you want to update the existing configuration? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return

            # Update existing configuration
            updated_config = ConfigurationService.update_configuration(
                db=db,
                config_id=existing_config.config_id,
                constitution_path=args.constitution,
                history_path=args.history,
                spec_folder=args.spec_folder,
                docs_folder=args.docs_folder,
                assets_folder=args.assets_folder,
                root_folder=args.root_folder
            )
            print(f"Configuration updated successfully with ID: {updated_config.config_id}")
        else:
            # Create new configuration
            new_config = ConfigurationService.create_configuration(
                db=db,
                constitution_path=args.constitution,
                history_path=args.history,
                spec_folder=args.spec_folder,
                docs_folder=args.docs_folder,
                assets_folder=args.assets_folder,
                root_folder=args.root_folder
            )
            print(f"Configuration created successfully with ID: {new_config.config_id}")

    except Exception as e:
        print(f"Error creating/updating configuration: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    memorize_paths()