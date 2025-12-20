from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from src.config.settings import settings


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_cluster_url,
            api_key=settings.qdrant_api_key,
            https=True,
            timeout=60  # Set timeout to 60 seconds
        )
        self.collection_name = settings.qdrant_collection_name
    
    def create_collection(self):
        """Create a collection for storing book content embeddings"""
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=1024,  # Cohere embedding dimension
                distance=models.Distance.COSINE
            ),
            # Define payload schema for book content metadata
            optimizers_config=models.OptimizersConfigDiff(
                memmap_threshold=20000,
                indexing_threshold=20000,
            )
        )
    
    def upsert_vectors(self, vectors: List[Dict[str, Any]]):
        """Upsert vectors into the collection in batches to prevent timeouts"""
        # Create points
        points = [
            models.PointStruct(
                id=vector["id"],
                vector=vector["vector"],
                payload=vector["payload"]
            )
            for vector in vectors
        ]

        # Upsert in batches
        batch_size = 100  # Process in batches of 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
    
    def search_vectors(self, query_vector: List[float], top_k: int = 5):
        """Search for similar vectors in the collection"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )
        return results
    
    def delete_collection(self):
        """Delete the collection (useful for reindexing)"""
        self.client.delete_collection(collection_name=self.collection_name)


# Global instance
qdrant_service = QdrantService()