import asyncio
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import tiktoken

from src.services.openai_service import OpenAIService, ChatResponse
from src.vector_store import qdrant_client
from src.config import settings


@dataclass
class DocumentChunk:
    """Data class to represent a document chunk."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResults:
    """Data class to represent search results."""
    chunks: List[DocumentChunk]
    scores: List[float]


class EmbeddingService:
    """Service class for document chunking and embedding."""

    def __init__(self):
        self.openai_service = OpenAIService()
        self.logger = logging.getLogger(__name__)
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 512,
        overlap: int = 50,
        chunk_by: str = "tokens"
    ) -> List[DocumentChunk]:
        """
        Split text into chunks of specified size.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (in tokens or characters)
            overlap: Number of tokens/characters to overlap between chunks
            chunk_by: How to chunk - 'tokens' or 'characters'

        Returns:
            List of DocumentChunk objects
        """
        if chunk_by == "tokens":
            tokens = self.tokenizer.encode(text)
            chunks = []
            start_idx = 0

            while start_idx < len(tokens):
                end_idx = start_idx + chunk_size
                chunk_tokens = tokens[start_idx:end_idx]

                # Convert tokens back to text
                chunk_text = self.tokenizer.decode(chunk_tokens)

                # Add overlap for next chunk
                start_idx = end_idx - overlap if end_idx < len(tokens) else len(tokens)

                chunk_id = hashlib.md5(f"{chunk_text[:50]}_{len(chunks)}".encode()).hexdigest()
                chunk = DocumentChunk(
                    id=chunk_id,
                    content=chunk_text,
                    metadata={"start_token": start_idx, "end_token": end_idx}
                )
                chunks.append(chunk)

        else:  # chunk_by == "characters"
            chunks = []
            start_idx = 0

            while start_idx < len(text):
                end_idx = start_idx + chunk_size
                chunk_text = text[start_idx:end_idx]

                # Add overlap for next chunk
                start_idx = end_idx - overlap if end_idx < len(text) else len(text)

                chunk_id = hashlib.md5(f"{chunk_text[:50]}_{len(chunks)}".encode()).hexdigest()
                chunk = DocumentChunk(
                    id=chunk_id,
                    content=chunk_text,
                    metadata={"start_char": start_idx, "end_char": end_idx}
                )
                chunks.append(chunk)

        return chunks

    def chunk_document(
        self,
        content: str,
        doc_id: str,
        title: str = "",
        source: str = "",
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[DocumentChunk]:
        """
        Chunk a document with metadata.

        Args:
            content: Document content to chunk
            doc_id: Document ID
            title: Document title
            source: Document source/path
            chunk_size: Size of each chunk
            overlap: Number of tokens to overlap between chunks

        Returns:
            List of DocumentChunk objects with metadata
        """
        chunks = self.chunk_text(content, chunk_size, overlap)

        # Add document-specific metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "doc_id": doc_id,
                "title": title,
                "source": source,
                "chunk_index": i,
                "total_chunks": len(chunks)
            })

        return chunks

    async def generate_embeddings(
        self,
        chunks: List[DocumentChunk],
        model: str = "text-embedding-ada-002"
    ) -> List[DocumentChunk]:
        """
        Generate embeddings for document chunks.

        Args:
            chunks: List of DocumentChunk objects
            model: OpenAI embedding model to use

        Returns:
            List of DocumentChunk objects with embeddings
        """
        # Extract content from chunks
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings in batches to respect API limits
        batch_size = 20  # OpenAI's max batch size is typically 2048, but we'll be conservative
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = await self.openai_service.generate_embeddings(batch_texts, model)
            all_embeddings.extend(batch_embeddings)

        # Update chunks with embeddings
        for chunk, embedding in zip(chunks, all_embeddings):
            chunk.embedding = embedding

        return chunks

    async def index_document_chunks(
        self,
        chunks: List[DocumentChunk],
        collection_name: str = "textbook_content"
    ) -> bool:
        """
        Index document chunks in Qdrant vector store.

        Args:
            chunks: List of DocumentChunk objects with embeddings
            collection_name: Name of the Qdrant collection

        Returns:
            True if indexing was successful, False otherwise
        """
        try:
            from qdrant_client.http import models

            # Create collection if it doesn't exist
            from src.vector_store.qdrant_client import create_collection_if_not_exists
            create_collection_if_not_exists(collection_name)

            # Prepare points for insertion
            points = []
            for chunk in chunks:
                if chunk.embedding is None:
                    self.logger.warning(f"Chunk {chunk.id} has no embedding, skipping")
                    continue

                points.append(models.PointStruct(
                    id=chunk.id,
                    vector=chunk.embedding,
                    payload={
                        "content": chunk.content,
                        "metadata": chunk.metadata
                    }
                ))

            if points:
                # Upload points to Qdrant
                qdrant_client.upsert(
                    collection_name=collection_name,
                    points=points
                )

            return True

        except Exception as e:
            self.logger.error(f"Error indexing document chunks: {str(e)}")
            return False

    async def search(
        self,
        query: str,
        collection_name: str = "textbook_content",
        top_k: int = 5,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> SearchResults:
        """
        Search for relevant chunks in the vector store.

        Args:
            query: Search query
            collection_name: Name of the Qdrant collection
            top_k: Number of top results to return
            filter_conditions: Optional filter conditions

        Returns:
            SearchResults object with relevant chunks and scores
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.openai_service.generate_embeddings([query])
            query_vector = query_embedding[0]  # Get the first (and only) embedding

            # Prepare filter if provided
            qdrant_filter = None
            if filter_conditions:
                filter_conditions_list = []
                for key, value in filter_conditions.items():
                    filter_conditions_list.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value)
                        )
                    )

                if filter_conditions_list:
                    qdrant_filter = models.Filter(must=filter_conditions_list)

            # Search in Qdrant
            search_results = qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=qdrant_filter,
                with_payload=True
            )

            # Convert results to DocumentChunk objects
            chunks = []
            scores = []
            for result in search_results:
                payload = result.payload
                chunk = DocumentChunk(
                    id=result.id,
                    content=payload.get("content", ""),
                    metadata=payload.get("metadata", {}),
                    embedding=None  # Don't include embedding to save space
                )
                chunks.append(chunk)
                scores.append(result.score)

            return SearchResults(chunks=chunks, scores=scores)

        except Exception as e:
            self.logger.error(f"Error searching in vector store: {str(e)}")
            return SearchResults(chunks=[], scores=[])

    async def process_document(
        self,
        content: str,
        doc_id: str,
        title: str = "",
        source: str = "",
        collection_name: str = "textbook_content",
        chunk_size: int = 512,
        overlap: int = 50
    ) -> bool:
        """
        Complete pipeline: chunk, embed, and index a document.

        Args:
            content: Document content
            doc_id: Document ID
            title: Document title
            source: Document source
            collection_name: Qdrant collection name
            chunk_size: Size of each chunk
            overlap: Number of tokens to overlap

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Step 1: Chunk the document
            chunks = self.chunk_document(
                content=content,
                doc_id=doc_id,
                title=title,
                source=source,
                chunk_size=chunk_size,
                overlap=overlap
            )

            self.logger.info(f"Document {doc_id} chunked into {len(chunks)} chunks")

            # Step 2: Generate embeddings
            chunks_with_embeddings = await self.generate_embeddings(chunks)
            self.logger.info(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")

            # Step 3: Index in vector store
            success = await self.index_document_chunks(chunks_with_embeddings, collection_name)
            self.logger.info(f"Indexing result for {doc_id}: {'Success' if success else 'Failed'}")

            return success

        except Exception as e:
            self.logger.error(f"Error processing document {doc_id}: {str(e)}")
            return False

    def calculate_chunk_stats(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Calculate statistics for a list of chunks.

        Args:
            chunks: List of DocumentChunk objects

        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "avg_tokens_per_chunk": 0,
                "total_chars": 0,
                "avg_chars_per_chunk": 0
            }

        total_tokens = sum(len(self.tokenizer.encode(chunk.content)) for chunk in chunks)
        total_chars = sum(len(chunk.content) for chunk in chunks)

        return {
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "avg_tokens_per_chunk": total_tokens / len(chunks),
            "total_chars": total_chars,
            "avg_chars_per_chunk": total_chars / len(chunks)
        }

    async def batch_process_documents(
        self,
        documents: List[Dict[str, Any]],
        collection_name: str = "textbook_content"
    ) -> Dict[str, Any]:
        """
        Process multiple documents in batch.

        Args:
            documents: List of documents with keys: 'content', 'doc_id', 'title', 'source'
            collection_name: Qdrant collection name

        Returns:
            Dictionary with processing results
        """
        results = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "failed_documents": [],
            "total_chunks": 0
        }

        for doc in documents:
            try:
                success = await self.process_document(
                    content=doc.get('content', ''),
                    doc_id=doc.get('doc_id', ''),
                    title=doc.get('title', ''),
                    source=doc.get('source', ''),
                    collection_name=collection_name
                )

                results["processed"] += 1
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["failed_documents"].append(doc.get('doc_id', 'unknown'))

            except Exception as e:
                results["failed"] += 1
                results["failed_documents"].append(doc.get('doc_id', 'unknown'))
                self.logger.error(f"Error processing document {doc.get('doc_id', 'unknown')}: {str(e)}")

        return results

    async def delete_document_from_index(
        self,
        doc_id: str,
        collection_name: str = "textbook_content"
    ) -> bool:
        """
        Delete all chunks belonging to a document from the vector store.

        Args:
            doc_id: Document ID to delete
            collection_name: Name of the Qdrant collection

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Find all points with this document ID
            search_results = qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.doc_id",
                            match=models.MatchValue(value=doc_id)
                        )
                    ]
                ),
                limit=10000  # Adjust based on expected max chunks per document
            )

            # Extract point IDs
            point_ids = [point.id for point in search_results[0]]

            if point_ids:
                # Delete the points
                qdrant_client.delete(
                    collection_name=collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )

            return True

        except Exception as e:
            self.logger.error(f"Error deleting document {doc_id} from index: {str(e)}")
            return False


# Global instance
embedding_service = EmbeddingService()