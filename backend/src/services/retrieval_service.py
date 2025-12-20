from typing import List, Dict, Any
from src.config.qdrant_config import qdrant_service
from src.services.embedding_service import embedding_service
from src.models.entities import RetrievedChunk
from src.config.settings import settings


class RetrievalService:
    def __init__(self):
        self.qdrant_service = qdrant_service
        self.embedding_service = embedding_service
        self.top_k = settings.retrieval_top_k
        self.score_threshold = 0.0

        # self.score_threshold = settings.retrieval_score_threshold
    
    def retrieve_relevant_chunks(self, query: str, book_id: str = None) -> List[RetrievedChunk]:
        """Retrieve relevant chunks from the vector database"""
        # Generate embedding for the query
        # query_embedding = self.embedding_service.generate_embeddings([query])[0]  
        # query_embedding = self.embedding_service.embed_query(query)
        query_embedding = self.embedding_service.embed_text(query)


        # Search in Qdrant
        search_results = self.qdrant_service.search_vectors(
            query_vector=query_embedding,
            top_k=self.top_k
        )
        
        # Filter by book_id if specified
        if book_id:
            search_results = [
                result for result in search_results
                if result.payload.get("book_id") == book_id
            ]
    #    ================================================================
        print(f"[RAG] Raw Qdrant results: {len(search_results)}")
    #    ================================================================

        # Filter by score threshold
        filtered_results = [
            result for result in search_results
            if result.score >= self.score_threshold
        ]
        
        # Convert to RetrievedChunk objects
        retrieved_chunks = []
        for result in filtered_results:
            chunk = RetrievedChunk(
                chunk_id=result.payload.get("chunk_id"),
                book_id=result.payload.get("book_id"),
                chapter=result.payload.get("chapter"),
                section=result.payload.get("section"),
                paragraph_index=result.payload.get("paragraph_index"),
                content=result.payload.get("content", ""),
                relevance_score=result.score,
                metadata={
                    k: v for k, v in result.payload.items()
                    if k not in ["chunk_id", "book_id", "chapter", "section",
                                "paragraph_index", "content"]
                }
            )

            # chunk = RetrievedChunk(
            #     chunk_id=result.payload["chunk_id"],
            #     book_id=result.payload["book_id"],
            #     chapter=result.payload["chapter"],
            #     section=result.payload["section"],
            #     paragraph_index=result.payload["paragraph_index"],
            #     content=result.payload["content"],
            #     relevance_score=result.score,
            #     metadata={
            #         k: v for k, v in result.payload.items()
            #         if k not in ["chunk_id", "book_id", "chapter", "section", 
            #                     "paragraph_index", "content"]
            #     }
            # )
    #    ================================================================
            print(f"[RAG] After score filter: {len(filtered_results)}")

    #    ================================================================
            
            retrieved_chunks.append(chunk)
        
        return retrieved_chunks


# Global instance
retrieval_service = RetrievalService()