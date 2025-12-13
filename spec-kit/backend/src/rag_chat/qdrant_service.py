"""
Qdrant vector database service for RAG functionality
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid
from .config import rag_settings


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=rag_settings.qdrant_url,
            api_key=rag_settings.qdrant_api_key,
            prefer_grpc=False  # Using REST API
        )
        self.collection_name = rag_settings.qdrant_collection_name

    def create_collection(self):
        """
        Create the collection if it doesn't exist
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
            print(f"Collection {self.collection_name} already exists")
        except:
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1024,  # Cohere embedding dimension
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection {self.collection_name}")

    def upsert_vectors(self, texts: List[str], embeddings: List[List[float]],
                      doc_ids: List[str], metadatas: List[Dict[str, Any]]):
        """
        Upsert vectors to Qdrant with metadata
        """
        points = []
        for i, (text, embedding, doc_id, metadata) in enumerate(zip(texts, embeddings, doc_ids, metadatas)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    "doc_id": doc_id,
                    **metadata  # Include additional metadata
                }
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search_vectors(self, query_embedding: List[float], top_k: int = 5,
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant
        """
        # Build filter conditions
        qdrant_filter = None
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if isinstance(value, list):
                    # Handle array filters
                    condition = models.FieldCondition(
                        key=key,
                        match=models.MatchAny(any=value)
                    )
                else:
                    # Handle single value filters
                    condition = models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                filter_conditions.append(condition)

            if filter_conditions:
                qdrant_filter = models.Filter(
                    must=filter_conditions
                )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "text": result.payload.get("text", ""),
                "doc_id": result.payload.get("doc_id", ""),
                "score": result.score,
                "metadata": {k: v for k, v in result.payload.items() if k not in ["text", "doc_id"]}
            })

        return formatted_results

    def delete_collection(self):
        """
        Delete the collection (useful for reindexing)
        """
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Deleted collection {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")

    def get_collection_info(self):
        """
        Get information about the collection
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vector_size": collection_info.config.params.vectors.size,
                "points_count": collection_info.points_count
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return None