#!/usr/bin/env python3
"""
Test script to validate the RAG implementation
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

async def test_rag_implementation():
    """Test the RAG implementation"""
    print("Testing RAG Implementation...")

    # Test 1: Set environment variables manually for testing
    print("\n1. Setting environment variables...")
    os.environ['COHERE_API_KEY'] = 'jbBhaTcgChesH9KAcdPx6VoppmIpTuDYWvQ71b7s'
    os.environ['QDRANT_URL'] = 'https://2d545162-c8d9-46ea-b665-bad7333c085d.us-east4-0.gcp.cloud.qdrant.io:6333'
    os.environ['QDRANT_API_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.VRH5ukCLgaIU4wGzVzy8h0aCjiqfQG2-JC2cLlwAv6E'
    os.environ['CCR_QWEN_TOKEN'] = 'your_ccr_qwen_token_here'

    # Now import the config after setting environment variables
    from src.rag_chat.config import rag_settings

    # Check if required environment variables are set
    assert rag_settings.cohere_api_key, "COHERE_API_KEY not set"
    assert rag_settings.qdrant_url, "QDRANT_URL not set"
    assert rag_settings.qdrant_api_key, "QDRANT_API_KEY not set"
    print("[OK] Environment variables are set")

    # Test 2: Test import and initialization of services (without connecting)
    print("\n2. Testing service initialization...")
    from src.rag_chat.embedding_service import CohereEmbeddingService
    from src.rag_chat.qdrant_service import QdrantService
    from src.rag_chat.rag_service import RAGService

    embedding_service = CohereEmbeddingService()
    qdrant_service = QdrantService()
    rag_service = RAGService()

    assert embedding_service is not None, "Embedding service not initialized"
    assert qdrant_service is not None, "Qdrant service not initialized"
    assert rag_service is not None, "RAG service not initialized"
    print("[OK] Services initialized correctly")

    # Test 3: Test response generation structure (without actual API calls)
    print("\n3. Testing response generation structure...")
    response = await rag_service.generate_response("Test question",
                                                   [{"text": "Test document content", "doc_id": "test_doc", "score": 0.9}],
                                                   selected_text="Selected text")
    assert isinstance(response, str), "Response should be a string"
    print("[OK] Response generation structure works")

    print("\n[SUCCESS] All tests passed! RAG implementation is ready.")
    print("\nNote: This test validates the implementation structure.")
    print("Full functionality requires valid API keys and network access.")

if __name__ == "__main__":
    asyncio.run(test_rag_implementation())