from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.schemas import ConfigurationCreate, ConfigurationUpdate, Configuration as ConfigurationSchema
from src.services.configuration_service import ConfigurationService

router = APIRouter()


@router.post("/", response_model=ConfigurationSchema)
def create_configuration(
    configuration: ConfigurationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new configuration.
    """
    db_configuration = ConfigurationService.get_configuration_by_path(
        db, configuration.docs_folder
    )
    if db_configuration:
        raise HTTPException(
            status_code=400,
            detail="Configuration with this docs folder already exists"
        )
    return ConfigurationService.create_configuration(
        db=db,
        constitution_path=configuration.constitution_path,
        history_path=configuration.history_path,
        spec_folder=configuration.spec_folder,
        docs_folder=configuration.docs_folder,
        assets_folder=configuration.assets_folder,
        root_folder=configuration.root_folder
    )


@router.get("/{config_id}", response_model=ConfigurationSchema)
def read_configuration(config_id: str, db: Session = Depends(get_db)):
    """
    Get configuration by ID.
    """
    configuration = ConfigurationService.get_configuration(db, config_id)
    if configuration is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return configuration


@router.put("/{config_id}", response_model=ConfigurationSchema)
def update_configuration(
    config_id: str,
    configuration_update: ConfigurationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing configuration.
    """
    updated_config = ConfigurationService.update_configuration(
        db=db,
        config_id=config_id,
        constitution_path=configuration_update.constitution_path,
        history_path=configuration_update.history_path,
        spec_folder=configuration_update.spec_folder,
        docs_folder=configuration_update.docs_folder,
        assets_folder=configuration_update.assets_folder,
        root_folder=configuration_update.root_folder
    )
    if updated_config is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return updated_config


@router.delete("/{config_id}")
def delete_configuration(config_id: str, db: Session = Depends(get_db)):
    """
    Delete a configuration.
    """
    deleted = ConfigurationService.delete_configuration(db, config_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return {"message": "Configuration deleted successfully"}