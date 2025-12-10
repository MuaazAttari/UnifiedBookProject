from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Optional, List, Dict, Any

from src.config import settings


def get_qdrant_client():
    """
    Create and return a Qdrant client instance based on configuration.
    """
    if settings.QDRANT_URL and settings.QDRANT_API_KEY:
        # Use cloud instance
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=True
        )
    else:
        # Use local instance
        client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )

    return client


# Create a global client instance
qdrant_client = get_qdrant_client()


def create_collection_if_not_exists(collection_name: str, vector_size: int = 1536):
    """
    Create a collection in Qdrant if it doesn't exist.

    Args:
        collection_name: Name of the collection to create
        vector_size: Size of the vectors to be stored (default 1536 for OpenAI embeddings)
    """
    try:
        # Check if collection exists
        qdrant_client.get_collection(collection_name)
    except:
        # Collection doesn't exist, create it
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )


class QdrantService:
    """
    Service class for enhanced Qdrant operations specific to the RAG system.
    """

    def __init__(self):
        self.client = qdrant_client
        self.default_collection = "textbook_content"

    def create_textbook_collection(self, collection_name: Optional[str] = None) -> bool:
        """
        Create a collection specifically for textbook content.

        Args:
            collection_name: Name of the collection (uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        try:
            name = collection_name or self.default_collection
            create_collection_if_not_exists(name, vector_size=1536)  # OpenAI ada embedding size
            return True
        except Exception as e:
            print(f"Error creating collection {collection_name}: {str(e)}")
            return False

    def upsert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Upsert vectors into a collection.

        Args:
            vectors: List of vectors to upsert
            payloads: List of payloads corresponding to each vector
            ids: List of IDs for the vectors (auto-generated if not provided)
            collection_name: Name of the collection

        Returns:
            True if successful, False otherwise
        """
        try:
            name = collection_name or self.default_collection

            # Generate IDs if not provided
            if ids is None:
                from uuid import uuid4
                ids = [str(uuid4()) for _ in range(len(vectors))]

            # Prepare points
            points = [
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
                for point_id, vector, payload in zip(ids, vectors, payloads)
            ]

            # Upsert points
            self.client.upsert(
                collection_name=name,
                points=points
            )

            return True
        except Exception as e:
            print(f"Error upserting vectors: {str(e)}")
            return False

    def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 10,
        collection_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: Query vector
            top_k: Number of results to return
            collection_name: Name of the collection
            filters: Optional filters for search

        Returns:
            List of search results with payload and score
        """
        try:
            name = collection_name or self.default_collection

            # Prepare filter if provided
            qdrant_filter = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )

                if filter_conditions:
                    qdrant_filter = models.Filter(must=filter_conditions)

            # Perform search
            results = self.client.search(
                collection_name=name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=qdrant_filter,
                with_payload=True
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result.id,
                    'score': result.score,
                    'payload': result.payload
                })

            return formatted_results
        except Exception as e:
            print(f"Error searching vectors: {str(e)}")
            return []

    def delete_by_payload(
        self,
        key: str,
        value: Any,
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Delete points from collection based on payload value.

        Args:
            key: Payload key to match
            value: Payload value to match
            collection_name: Name of the collection

        Returns:
            True if successful, False otherwise
        """
        try:
            name = collection_name or self.default_collection

            # Find points matching the criteria
            scroll_results = self.client.scroll(
                collection_name=name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    ]
                ),
                limit=10000  # Adjust based on expected max matches
            )

            # Extract point IDs
            point_ids = [point.id for point in scroll_results[0]]

            if point_ids:
                # Delete the points
                self.client.delete(
                    collection_name=name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )

            return True
        except Exception as e:
            print(f"Error deleting by payload: {str(e)}")
            return False

    def get_collection_info(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection information
        """
        try:
            name = collection_name or self.default_collection
            collection_info = self.client.get_collection(name)

            return {
                'name': collection_info.config.params.vectors_count,
                'vector_count': collection_info.vectors_count,
                'indexed_vector_count': collection_info.indexed_vectors_count,
                'points_count': collection_info.points_count
            }
        except Exception as e:
            print(f"Error getting collection info: {str(e)}")
            return {}

    def recreate_collection(self, collection_name: Optional[str] = None) -> bool:
        """
        Recreate a collection (delete and create again).

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful, False otherwise
        """
        try:
            name = collection_name or self.default_collection

            # Delete collection if it exists
            try:
                self.client.delete_collection(name)
            except:
                pass  # Collection might not exist, which is fine

            # Create new collection
            self.create_textbook_collection(name)

            return True
        except Exception as e:
            print(f"Error recreating collection: {str(e)}")
            return False


# Global instance
qdrant_service = QdrantService()