from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.database import get_db
from src.schemas import ChatSession as ChatSessionSchema, ChatSessionCreate
from src.services.rag_service import rag_service, RAGResponse
from src.services.chat_session_service import ChatSessionService
from src.services.openai_service import ChatResponse
from src.utils.query_sanitizer import QuerySanitizer

router = APIRouter()


@router.post("/", response_model=ChatSessionSchema)
async def create_chat_session(
    chat_session: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new chat session.
    """
    # Validate the context type
    if chat_session.context_type not in ["full_book", "selected_text"]:
        raise HTTPException(
            status_code=400,
            detail="context_type must be either 'full_book' or 'selected_text'"
        )

    # Sanitize and validate the query
    try:
        sanitized_query = QuerySanitizer.validate_query(chat_session.query)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query: {str(e)}"
        )

    # Sanitize selected text if provided
    sanitized_selected_text = None
    if chat_session.selected_text:
        sanitized_selected_text = QuerySanitizer.sanitize_context(chat_session.selected_text)

    # Create the chat session
    db_chat_session = ChatSessionService.create_chat_session(
        db=db,
        user_id=chat_session.user_id,
        query=sanitized_query,
        response="",  # Will be populated after processing
        context_type=chat_session.context_type,
        selected_text=sanitized_selected_text
    )

    # Process the query using RAG
    try:
        if chat_session.context_type == "full_book":
            rag_response = await rag_service.process_full_book_query(
                query=sanitized_query,
                user_id=chat_session.user_id
            )
        else:  # selected_text
            if not sanitized_selected_text:
                raise HTTPException(
                    status_code=400,
                    detail="selected_text is required when context_type is 'selected_text'"
                )
            rag_response = await rag_service.process_selected_text_query(
                query=sanitized_query,
                selected_text=sanitized_selected_text,
                user_id=chat_session.user_id
            )

        # Update the chat session with the original answer (unformatted for storage)
        updated_session = ChatSessionService.update_chat_session(
            db=db,
            session_id=db_chat_session.session_id,
            response=rag_response.answer,
            tokens_used=rag_response.tokens_used
        )

        return updated_session

    except Exception as e:
        # If RAG processing fails, update the session with error info
        ChatSessionService.update_chat_session(
            db=db,
            session_id=db_chat_session.session_id,
            response=f"Error processing query: {str(e)}",
            tokens_used=0
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=RAGResponse)
async def process_query(
    query: str = Query(..., min_length=1, max_length=1000, description="User query"),
    context_type: str = Query("full_book", regex="^(full_book|selected_text)$", description="Type of context to use"),
    selected_text: Optional[str] = Query(None, max_length=5000, description="Selected text for context (required if context_type is selected_text)"),
    user_id: Optional[str] = Query(None, description="User ID for tracking"),
    max_context_length: int = Query(2000, ge=500, le=5000, description="Maximum context length"),
    top_k: int = Query(5, ge=1, le=20, description="Number of top results to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Process a query using RAG and return the response with context and sources.
    """
    # Sanitize and validate the query
    try:
        sanitized_query = QuerySanitizer.validate_query(query)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query: {str(e)}"
        )

    # Sanitize selected text if provided
    sanitized_selected_text = selected_text
    if selected_text:
        sanitized_selected_text = QuerySanitizer.sanitize_context(selected_text)

    # Validate inputs
    if context_type == "selected_text" and not sanitized_selected_text:
        raise HTTPException(
            status_code=400,
            detail="selected_text is required when context_type is 'selected_text'"
        )

    try:
        # Process the query using RAG
        if context_type == "full_book":
            rag_response = await rag_service.process_full_book_query(
                query=sanitized_query,
                user_id=user_id,
                max_context_length=max_context_length,
                top_k=top_k
            )
        else:  # selected_text
            rag_response = await rag_service.process_selected_text_query(
                query=sanitized_query,
                selected_text=sanitized_selected_text,
                user_id=user_id
            )

        # Create a chat session record
        ChatSessionService.create_chat_session(
            db=db,
            user_id=user_id,
            query=sanitized_query,
            response=rag_response.answer,
            context_type=context_type,
            selected_text=sanitized_selected_text,
            tokens_used=rag_response.tokens_used
        )

        # Format the response for display
        formatted_response = rag_service.format_response(rag_response)
        return rag_response  # Return the original RAGResponse to maintain API contract

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/{session_id}", response_model=ChatSessionSchema)
def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific chat session by ID.
    """
    chat_session = ChatSessionService.get_chat_session(db, session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return chat_session


@router.get("/", response_model=List[ChatSessionSchema])
def get_chat_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get chat sessions with optional filtering.
    """
    chat_sessions = ChatSessionService.get_chat_sessions(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    return chat_sessions


@router.get("/history/{user_id}", response_model=List[ChatSessionSchema])
def get_user_chat_history(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get chat history for a specific user.
    """
    chat_sessions = ChatSessionService.get_chat_sessions(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    if not chat_sessions:
        raise HTTPException(status_code=404, detail="No chat sessions found for this user")
    return chat_sessions


@router.delete("/{session_id}")
def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a specific chat session.
    """
    deleted = ChatSessionService.delete_chat_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"message": "Chat session deleted successfully"}


@router.post("/validate-query")
async def validate_query(query: str = Query(..., min_length=1, max_length=1000)):
    """
    Validate a query without processing it.
    """
    try:
        validated_query = QuerySanitizer.validate_query(query)
        return {"valid": True, "cleaned_query": validated_query}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating query: {str(e)}")


@router.post("/find-relevant-chapters")
async def find_relevant_chapters(
    query: str = Query(..., min_length=1, max_length=1000),
    top_k: int = Query(3, ge=1, le=10, description="Number of top chapters to return")
):
    """
    Find the most relevant chapters for a given query.
    """
    # Sanitize and validate the query
    try:
        sanitized_query = QuerySanitizer.validate_query(query)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query: {str(e)}"
        )

    try:
        relevant_chapters = await rag_service.get_relevant_chapters(sanitized_query, top_k)
        return {"chapters": relevant_chapters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding relevant chapters: {str(e)}")