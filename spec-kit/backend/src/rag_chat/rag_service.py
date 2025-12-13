"""
Main RAG service that orchestrates embedding, vector storage, and retrieval
"""
from typing import List, Dict, Any, Optional
from .embedding_service import CohereEmbeddingService
from .qdrant_service import QdrantService
from .config import rag_settings
from ..database.session import get_db
from ..models.user import User
from .models import ChatSession, ChatMessage
from sqlalchemy.orm import Session
import asyncio
import logging


logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.embedding_service = CohereEmbeddingService()
        self.qdrant_service = QdrantService()
        self.top_k = rag_settings.rag_default_topk

    def initialize(self):
        """
        Initialize the RAG service by creating collections if they don't exist
        """
        self.qdrant_service.create_collection()

    async def ingest_document(self, doc_id: str, text_chunks: List[str],
                            metadata: List[Dict[str, Any]] = None):
        """
        Ingest document chunks into vector database
        """
        if metadata is None:
            metadata = [{}] * len(text_chunks)

        # Embed the text chunks
        embeddings = await self.embedding_service.embed_texts(text_chunks)

        # Upsert to Qdrant
        doc_ids = [doc_id] * len(text_chunks)
        self.qdrant_service.upsert_vectors(text_chunks, embeddings, doc_ids, metadata)

        logger.info(f"Ingested {len(text_chunks)} chunks for document {doc_id}")

    async def query(self, query_text: str, filters: Optional[Dict[str, Any]] = None,
                   top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query the vector database and return relevant documents
        """
        if top_k is None:
            top_k = self.top_k

        # Embed the query
        query_embedding = await self.embedding_service.embed_query(query_text)

        # Search in Qdrant
        results = self.qdrant_service.search_vectors(
            query_embedding,
            top_k=top_k,
            filters=filters
        )

        return results

    async def generate_response(self, query: str, retrieved_docs: List[Dict[str, Any]],
                              selected_text: Optional[str] = None) -> str:
        """
        Generate a response using the retrieved documents and CCR Qwen
        """
        import httpx
        import json

        # Build context from retrieved documents
        context = "\n\n".join([doc["text"] for doc in retrieved_docs])

        # If there's selected text, include it as well
        if selected_text:
            context = f"User selected text: {selected_text}\n\nRelevant context:\n{context}"

        # Prepare the prompt for CCR Qwen
        prompt = f"""You are an AI assistant helping users with questions about physical AI and humanoid robotics.
        Use the following context to answer the user's question. If the context doesn't contain enough information,
        say so. Always provide citations to the source material when possible.

        Context:
        {context}

        Question: {query}

        Answer:"""

        # Call CCR Qwen endpoint
        headers = {
            "Authorization": f"Bearer {rag_settings.ccr_qwen_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen",  # or whatever the correct model identifier is
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": rag_settings.max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    rag_settings.ccr_qwen_url,
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    # Extract the actual response text from the API response
                    # The exact structure may vary depending on the CCR API format
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                    elif 'response' in result:
                        return result['response']
                    else:
                        # Fallback to returning the full response if format is unexpected
                        return str(result)
                else:
                    logger.error(f"CCR Qwen API error: {response.status_code} - {response.text}")
                    # Return a safe fallback response
                    return f"I'm sorry, I encountered an error processing your request. Here's what I can infer from the context: {query}"
        except Exception as e:
            logger.error(f"Error calling CCR Qwen API: {e}")
            # Return a safe fallback response
            return f"I'm sorry, I'm having trouble generating a response right now. Please try rephrasing your question: {query}"

    def create_session(self, db: Session, user_id: Optional[str] = None) -> ChatSession:
        """
        Create a new chat session
        """
        session = ChatSession(user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def add_message_to_session(self, db: Session, session_id: str, role: str,
                             content: str, user_id: Optional[str] = None,
                             retrieved_context: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """
        Add a message to a chat session
        """
        message = ChatMessage(
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
            retrieved_context=retrieved_context
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_session_messages(self, db: Session, session_id: str) -> List[ChatMessage]:
        """
        Get all messages for a session
        """
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()

    async def chat_query(self, query: str, session_id: str, db: Session,
                        user_id: Optional[str] = None, selected_text: Optional[str] = None,
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete chat query workflow: retrieve, generate response, and save to session
        """
        # Retrieve relevant documents
        retrieved_docs = await self.query(query, filters=filters)

        # Generate response
        response = await self.generate_response(query, retrieved_docs, selected_text)

        # Save user message to session
        user_message = self.add_message_to_session(
            db, session_id, "user", query, user_id,
            {"retrieved_docs": [doc["id"] for doc in retrieved_docs]}
        )

        # Save assistant response to session
        assistant_message = self.add_message_to_session(
            db, session_id, "assistant", response, user_id,
            {"retrieved_docs": [doc["id"] for doc in retrieved_docs]}
        )

        return {
            "response": response,
            "retrieved_docs": retrieved_docs,
            "user_message_id": user_message.id,
            "message_id": assistant_message.id
        }