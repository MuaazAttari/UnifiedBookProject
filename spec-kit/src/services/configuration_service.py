import uuid
from typing import Optional

from sqlalchemy.orm import Session

from src.models.configuration import Configuration


class ConfigurationService:
    @staticmethod
    def get_configuration(db: Session, config_id: str) -> Optional[Configuration]:
        """
        Retrieve a configuration by ID.
        """
        return db.query(Configuration).filter(Configuration.config_id == config_id).first()

    @staticmethod
    def get_configuration_by_path(db: Session, docs_folder: str) -> Optional[Configuration]:
        """
        Retrieve a configuration by docs folder path.
        """
        return db.query(Configuration).filter(Configuration.docs_folder == docs_folder).first()

    @staticmethod
    def create_configuration(
        db: Session,
        constitution_path: str,
        history_path: str,
        spec_folder: str,
        docs_folder: str,
        assets_folder: str,
        root_folder: str
    ) -> Configuration:
        """
        Create a new configuration.
        """
        config_id = str(uuid.uuid4())
        db_configuration = Configuration(
            config_id=config_id,
            constitution_path=constitution_path,
            history_path=history_path,
            spec_folder=spec_folder,
            docs_folder=docs_folder,
            assets_folder=assets_folder,
            root_folder=root_folder
        )
        db.add(db_configuration)
        db.commit()
        db.refresh(db_configuration)
        return db_configuration

    @staticmethod
    def update_configuration(
        db: Session,
        config_id: str,
        constitution_path: Optional[str] = None,
        history_path: Optional[str] = None,
        spec_folder: Optional[str] = None,
        docs_folder: Optional[str] = None,
        assets_folder: Optional[str] = None,
        root_folder: Optional[str] = None
    ) -> Optional[Configuration]:
        """
        Update an existing configuration.
        """
        db_configuration = db.query(Configuration).filter(Configuration.config_id == config_id).first()
        if db_configuration:
            if constitution_path is not None:
                db_configuration.constitution_path = constitution_path
            if history_path is not None:
                db_configuration.history_path = history_path
            if spec_folder is not None:
                db_configuration.spec_folder = spec_folder
            if docs_folder is not None:
                db_configuration.docs_folder = docs_folder
            if assets_folder is not None:
                db_configuration.assets_folder = assets_folder
            if root_folder is not None:
                db_configuration.root_folder = root_folder

            db.commit()
            db.refresh(db_configuration)
        return db_configuration

    @staticmethod
    def delete_configuration(db: Session, config_id: str) -> bool:
        """
        Delete a configuration.
        """
        db_configuration = db.query(Configuration).filter(Configuration.config_id == config_id).first()
        if db_configuration:
            db.delete(db_configuration)
            db.commit()
            return True
        return False