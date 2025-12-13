#!/usr/bin/env python3
"""
Simple test script to validate the RAG implementation components
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

async def test_rag_components():
    """Test the RAG components in isolation"""
    print("Testing RAG Components...")

    # Set environment variables for RAG
    os.environ['COHERE_API_KEY'] = 'jbBhaTcgChesH9KAcdPx6VoppmIpTuDYWvQ71b7s'
    os.environ['QDRANT_URL'] = 'https://2d545162-c8d9-46ea-b665-bad7333c085d.us-east4-0.gcp.cloud.qdrant.io:6333'
    os.environ['QDRANT_API_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.VRH5ukCLgaIU4wGzVzy8h0aCjiqfQG2-JC2cLlwAv6E'
    os.environ['CCR_QWEN_TOKEN'] = 'your_ccr_qwen_token_here'
    os.environ['ENVIRONMENT'] = 'local'  # Needed to avoid validation errors
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
    os.environ['SECRET_KEY'] = 'test-secret-key'

    # Test 1: Import and test config
    print("\n1. Testing RAG configuration...")
    from src.rag_chat.config import rag_settings
    assert rag_settings.cohere_api_key, "COHERE_API_KEY not set"
    assert rag_settings.qdrant_url, "QDRANT_URL not set"
    assert rag_settings.qdrant_api_key, "QDRANT_API_KEY not set"
    print("[OK] RAG configuration loaded")

    # Test 2: Test response generation structure only (without full service initialization)
    print("\n2. Testing response generation logic...")
    from src.rag_chat.rag_service import RAGService

    # Create a mock RAG service to test the generate_response method
    rag_service = RAGService()

    # Test the generate_response method without calling external APIs
    response = await rag_service.generate_response("Test question",
                                                   [{"text": "Test document content", "doc_id": "test_doc", "score": 0.9}],
                                                   selected_text="Selected text")
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"
    print("[OK] Response generation works")

    # Test 3: Test the structure of the generate_response method
    print("\n3. Testing generate_response method structure...")
    # Check that the method properly handles the prompt creation
    import inspect
    sig = inspect.signature(rag_service.generate_response)
    params = list(sig.parameters.keys())
    assert 'query' in params, "generate_response should accept query parameter"
    assert 'retrieved_docs' in params, "generate_response should accept retrieved_docs parameter"
    assert 'selected_text' in params, "generate_response should accept selected_text parameter"
    print("[OK] Method signature is correct")

    print("\n[SUCCESS] All component tests passed!")
    print("\nNote: This validates the implementation structure.")
    print("Full functionality requires valid API keys and network access.")

if __name__ == "__main__":
    asyncio.run(test_rag_components())