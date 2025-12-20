import sys
import os

# Add backend root to PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.qdrant_config import qdrant_service

qdrant_service.delete_collection()
qdrant_service.create_collection()

print("Qdrant collection deleted and recreated successfully")
