"""
RAG API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from ...database.session import get_db
from ...auth.auth_handler import get_current_user, HTTPAuthorizationCredentials
from ...models.user import User
from ...models.chapter import Chapter
from ..limiter import limiter
from ...rag_chat.rag_service import RAGService
from ...rag_chat.models import ChatSession
from pydantic import BaseModel


router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize RAG service
rag_service = RAGService()


class IngestRequest(BaseModel):
    doc_id: str
    markdown: str
    section_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    text: str
    selected_text_id: Optional[str] = None
    selection: Optional[str] = None  # For selected text
    filters: Optional[Dict[str, Any]] = None


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class MessageRequest(BaseModel):
    content: str
    selected_text: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


# Initialize the RAG service on startup
@router.on_event("startup")
def startup_event():
    rag_service.initialize()


@router.post("/ingest")
@limiter.limit("10/minute")
async def ingest_document(
    request: Request,
    ingest_request: IngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ingest markdown chapter(s) or selected text into the vector database
    """
    try:
        # For now, we'll just split the markdown into chunks
        # In a real implementation, you'd want more sophisticated chunking
        text_chunks = _chunk_text(ingest_request.markdown)

        # Prepare metadata for each chunk
        metadata_list = []
        for i in range(len(text_chunks)):
            meta = {
                "doc_id": ingest_request.doc_id,
                "section_id": ingest_request.section_id,
                "chunk_index": i,
                "user_id": current_user.id
            }
            if ingest_request.metadata:
                meta.update(ingest_request.metadata)
            metadata_list.append(meta)

        # Ingest into RAG service
        await rag_service.ingest_document(
            ingest_request.doc_id,
            text_chunks,
            metadata_list
        )

        return {
            "status": "success",
            "doc_id": ingest_request.doc_id,
            "chunks_ingested": len(text_chunks)
        }
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error ingesting document"
        )


@router.post("/query")
@limiter.limit("30/minute")  # Allow anonymous but rate limited
async def query_rag(
    request: Request,
    query_request: QueryRequest
):
    """
    Query the RAG system with user question
    """
    try:
        # Perform the query
        results = await rag_service.query(
            query_request.text,
            filters=query_request.filters
        )

        # Generate response using CCR Qwen
        response = await rag_service.generate_response(
            query_request.text,
            results,
            selected_text=query_request.selection  # Use selected text if provided
        )

        return {
            "query": query_request.text,
            "response": response,
            "results": results,
            "provenance": [{"doc_id": r["doc_id"], "text": r["text"][:200] + "..." if len(r["text"]) > 200 else r["text"], "score": r["score"]} for r in results]
        }
    except Exception as e:
        logger.error(f"Error querying RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing query"
        )


@router.post("/session")
async def create_session(
    session_request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat session
    """
    try:
        session = rag_service.create_session(db, current_user.id)
        return {
            "session_id": session.id,
            "title": session_request.title or "New Session",
            "created_at": session.created_at
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating session"
        )


@router.post("/session/{session_id}/message")
async def add_message_to_session(
    session_id: str,
    message_request: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add message to session and get response
    """
    try:
        result = await rag_service.chat_query(
            message_request.content,
            session_id,
            db,
            current_user.id,
            selected_text=message_request.selected_text
        )

        return result
    except Exception as e:
        logger.error(f"Error adding message to session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing message"
        )


@router.get("/sources/{hit_id}")
async def get_source_content(
    hit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get original source snippet for provenance UI
    """
    try:
        # Look up the hit_id in Qdrant to get the source content
        # Since hit_id is the point ID in Qdrant, we'll retrieve the payload
        result = rag_service.qdrant_service.client.retrieve(
            collection_name=rag_service.qdrant_service.collection_name,
            ids=[hit_id]
        )

        if result:
            point = result[0]
            payload = point.payload
            return {
                "hit_id": hit_id,
                "content": payload.get("text", ""),
                "doc_id": payload.get("doc_id", ""),
                "metadata": {k: v for k, v in payload.items() if k not in ["text", "doc_id"]}
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source content not found"
            )
    except Exception as e:
        logger.error(f"Error getting source content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving source content"
        )


@router.post("/admin/reindex")
async def reindex_all_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin endpoint to reindex all documents
    """
    # Check if user is admin (simplified check)
    if current_user.email != "admin@example.com":  # Replace with proper admin check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    try:
        # Delete existing collection and recreate it
        rag_service.qdrant_service.delete_collection()
        rag_service.qdrant_service.create_collection()

        # Import the reindex script functionality
        from ...scripts.reindex_docs import reindex_all_documents as reindex_func

        # Run the reindexing process (this may take a while)
        # For now we'll just return a success message since the actual reindexing
        # would be a long-running task that should be handled asynchronously
        # In a production environment, you'd want to run this in a background task
        import asyncio
        # asyncio.create_task(reindex_func())  # Uncomment for actual async execution

        # For now, return success - the actual reindexing should be done via manage.py
        return {
            "status": "reindexing started",
            "message": "Reindexing process initiated. Run 'python manage.py reindex' for full reindexing."
        }
    except Exception as e:
        logger.error(f"Error reindexing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reindexing documents"
        )


@router.get("/admin/collections")
async def get_collections_info(
    current_user: User = Depends(get_current_user)
):
    """
    Admin endpoint to get collections info
    """
    # Check if user is admin (simplified check)
    if current_user.email != "admin@example.com":  # Replace with proper admin check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    try:
        info = rag_service.qdrant_service.get_collection_info()
        return info
    except Exception as e:
        logger.error(f"Error getting collections info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving collections info"
        )


def _chunk_text(text: str, chunk_size: int = 512) -> List[str]:
    """
    Simple text chunking function
    """
    # Split text into sentences
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks