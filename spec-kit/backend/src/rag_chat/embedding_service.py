"""
Cohere embedding service for RAG functionality
"""
import asyncio
from typing import List, Dict, Any, Optional
import cohere
from ..config.settings import settings
from .config import rag_settings


class CohereEmbeddingService:
    def __init__(self):
        if rag_settings.cohere_api_key:
            self.client = cohere.Client(rag_settings.cohere_api_key)
        else:
            self.client = None
        self.model = rag_settings.cohere_model

    async def embed_texts(self, texts: List[str], input_type: str = "search_document") -> List[List[float]]:
        """
        Embed a list of texts using Cohere

        Args:
            texts: List of text strings to embed
            input_type: Cohere input type (search_query, search_document, etc.)

        Returns:
            List of embedding vectors
        """
        if not self.client:
            # Return mock embeddings for development when API key is not available
            import numpy as np
            return [[0.0] * 1024 for _ in range(len(texts))]

        try:
            # Cohere's embed endpoint accepts up to 96 texts per request
            batch_size = 96
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type=input_type
                )
                all_embeddings.extend(response.embeddings)

            return all_embeddings
        except Exception as e:
            print(f"Error embedding texts: {e}")
            raise

    async def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query string
        """
        if not self.client:
            # Return mock embedding for development when API key is not available
            return [0.0] * 1024

        try:
            response = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query"
            )
            return response.embeddings[0]
        except Exception as e:
            print(f"Error embedding query: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the embedding dimension for the model
        """
        # For embed-english-v3.0, the dimension is 1024
        # We'll return this as a constant for now
        return 1024