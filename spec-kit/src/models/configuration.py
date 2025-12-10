from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from src.db.database import Base


class Configuration(Base):
    __tablename__ = "configurations"

    config_id = Column(String, primary_key=True, index=True)
    constitution_path = Column(String, nullable=False)
    history_path = Column(String, nullable=False)
    spec_folder = Column(String, nullable=False)
    docs_folder = Column(String, nullable=False)
    assets_folder = Column(String, nullable=False)
    root_folder = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())