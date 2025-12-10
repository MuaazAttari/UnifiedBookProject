from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConfigurationBase(BaseModel):
    constitution_path: str
    history_path: str
    spec_folder: str
    docs_folder: str
    assets_folder: str
    root_folder: str


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    constitution_path: Optional[str] = None
    history_path: Optional[str] = None
    spec_folder: Optional[str] = None
    docs_folder: Optional[str] = None
    assets_folder: Optional[str] = None
    root_folder: Optional[str] = None


class Configuration(ConfigurationBase):
    config_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True