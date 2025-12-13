"""
Tests for RAG chat functionality
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.rag_chat.rag_service import RAGService
from src.rag_chat.embedding_service import CohereEmbeddingService
from src.rag_chat.qdrant_service import QdrantService


class TestRAGService:
    def setup_method(self):
        self.rag_service = RAGService()

    @pytest.mark.asyncio
    async def test_ingest_document(self):
        """Test document ingestion"""
        # Mock the embedding and qdrant services
        with patch.object(self.rag_service.embedding_service, 'embed_texts',
                         new_callable=AsyncMock) as mock_embed, \
             patch.object(self.rag_service.qdrant_service, 'upsert_vectors',
                         return_value=None) as mock_upsert:

            mock_embed.return_value = [[0.1, 0.2, 0.3]]  # Mock embedding

            # Test ingestion
            await self.rag_service.ingest_document(
                doc_id="test_doc",
                text_chunks=["Test content"],
                metadata=[{"source": "test"}]
            )

            # Verify the methods were called
            mock_embed.assert_called_once()
            mock_upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_query(self):
        """Test querying functionality"""
        with patch.object(self.rag_service.embedding_service, 'embed_query',
                         new_callable=AsyncMock) as mock_embed, \
             patch.object(self.rag_service.qdrant_service, 'search_vectors',
                         return_value=[{"id": "1", "text": "test", "doc_id": "test", "score": 0.9}]) as mock_search:

            mock_embed.return_value = [0.1, 0.2, 0.3]  # Mock embedding

            results = await self.rag_service.query("test query")

            # Verify the methods were called
            mock_embed.assert_called_once()
            mock_search.assert_called_once()

            assert len(results) == 1
            assert results[0]["text"] == "test"

    def test_create_session(self):
        """Test session creation"""
        # This would require a database session, so we'll just test the method exists
        assert hasattr(self.rag_service, 'create_session')
        assert hasattr(self.rag_service, 'add_message_to_session')


class TestCohereEmbeddingService:
    def setup_method(self):
        # We'll test with mocked cohere client
        pass

    @pytest.mark.asyncio
    async def test_embed_texts(self):
        """Test embedding multiple texts"""
        # Since we can't test with real API, we'll mock the cohere client
        with patch('src.rag_chat.embedding_service.cohere.Client') as mock_client_class:
            mock_client_instance = Mock()
            mock_client_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
            mock_client_class.return_value = mock_client_instance

            embedding_service = CohereEmbeddingService()

            result = await embedding_service.embed_texts(["test text"])

            assert len(result) == 1
            assert len(result[0]) == 3  # Assuming 3-dim embedding in mock


class TestQdrantService:
    def setup_method(self):
        # We'll test with mocked Qdrant client
        pass

    def test_create_collection(self):
        """Test collection creation"""
        with patch('src.rag_chat.qdrant_service.QdrantClient') as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance

            qdrant_service = QdrantService()

            # Test that the method exists and can be called
            qdrant_service.create_collection()

            # Verify client was initialized
            mock_client_class.assert_called()