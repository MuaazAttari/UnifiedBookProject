# from fastapi import APIRouter, HTTPException
# from typing import List, Dict, Any
# from src.models.entities import UserQuery, ChatResponse
# from src.services.book_service import book_service
# from src.services.retrieval_service import retrieval_service
# from src.services.generation_service import generation_service
# from src.services.database_service import database_service
# from src.config.settings import settings
# import uuid
# from datetime import datetime
# import logging


# router = APIRouter()


# @router.post("/chat", response_model=ChatResponse)
# async def chat_with_book(user_query: UserQuery):
#     """Main endpoint for asking questions about book content with full-book retrieval"""

#     logger = logging.getLogger("rag_chatbot")

#     try:
#         # Generate query ID if not provided
#         if not user_query.query_id:
#             user_query.query_id = str(uuid.uuid4())

#         # Validate query text
#         if not user_query.query_text or not user_query.query_text.strip():
#             logger.warning(f"Invalid query received: empty query text")
#             raise HTTPException(
#                 status_code=400,
#                 detail="query_text cannot be empty"
#             )

#         # Log the incoming query
#         logger.info(f"Received query from session {user_query.session_id}: {user_query.query_text[:50]}...")

#         # Set timestamp if not provided
#         if not user_query.query_timestamp:
#             user_query.query_timestamp = datetime.utcnow()

#         # If in selected text mode, handle differently
#         if user_query.mode == "selected_text" and user_query.selected_text:
#             # This should ideally be handled by a different endpoint, but we'll include the logic here
#             logger.info("Processing in selected text mode")
#             return chat_with_selected_text_endpoint(user_query)

#         # Retrieve relevant content chunks
#         logger.info("Performing retrieval for query")
#         retrieved_chunks = retrieval_service.retrieve_relevant_chunks(
#             query=user_query.query_text
#         )

#         # Generate response using the retrieved context
#         if retrieved_chunks:
#             logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")
#             answer = generation_service.generate_response(
#                 query_text=user_query.query_text,
#                 retrieved_chunks=retrieved_chunks
#             )

#             # Create citations from retrieved chunks
#             citations = [
#                 {
#                     "chunk_id": chunk.chunk_id,
#                     "book_id": chunk.book_id,
#                     "chapter": chunk.chapter,
#                     "section": chunk.section,
#                     "paragraph_index": chunk.paragraph_index
#                 }
#                 for chunk in retrieved_chunks
#             ]
#         else:
#             # No relevant content found, return fallback response
#             logger.info("No relevant content found, returning fallback response")
#             answer = "This information is not available in the book."
#             citations = []

#         # Create and return the response
#         response_id = str(uuid.uuid4())
#         response = ChatResponse(
#             response_id=response_id,
#             query_id=user_query.query_id,
#             answer=answer,
#             citations=citations,
#             session_id=user_query.session_id,
#             is_fallback_response=(answer == "This information is not available in the book."),
#             based_on="full_book"
#         )

#         logger.info(f"Returning response {response_id} for query {user_query.query_id}")

#         # Log the query and response to the database
#         start_logging = datetime.utcnow()
#         try:
#             await database_service.log_query(
#                 query_id=user_query.query_id,
#                 query_text=user_query.query_text,
#                 response_id=response_id,
#                 response_text=answer,
#                 processing_time=(datetime.utcnow() - user_query.query_timestamp).total_seconds() if user_query.query_timestamp else None
#             )
#             logging_time = (datetime.utcnow() - start_logging).total_seconds()
#             logger.info(f"Query logged successfully, took {logging_time:.3f}s")
#         except Exception as e:
#             logger.error(f"Failed to log query to database: {str(e)}")
#             # Don't fail the request if logging fails

#         return response
#     except HTTPException:
#         # Re-raise HTTP exceptions as they are
#         logger.warning("HTTP exception in chat endpoint")
#         raise
#     except Exception as e:
#         # Handle unexpected errors
#         logger.error(f"Unexpected error in chat endpoint: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"An unexpected error occurred: {str(e)}"
#         )


# async def chat_with_selected_text_endpoint(user_query: UserQuery):
#     """Handle selected text mode queries"""
#     logger = logging.getLogger("rag_chatbot")

#     if user_query.mode == "selected_text" and user_query.selected_text:
#         logger.info(f"Processing selected text query for session {user_query.session_id}")

#         # Generate response using only the selected text as context
#         answer = generation_service.generate_response(
#             query_text=user_query.query_text,
#             retrieved_chunks=[],
#             selected_text=user_query.selected_text
#         )

#         # Create response for selected text mode
#         response_id = str(uuid.uuid4())
#         response = ChatResponse(
#             response_id=response_id,
#             query_id=user_query.query_id,
#             answer=answer,
#             citations=[],
#             session_id=user_query.session_id,
#             is_fallback_response=(answer == "This information is not available in the book."),
#             based_on="selected_text"
#         )

#         logger.info(f"Selected text response generated: {response.response_id}")

#         # Log the query and response to the database
#         start_logging = datetime.utcnow()
#         try:
#             await database_service.log_query(
#                 query_id=user_query.query_id,
#                 query_text=user_query.query_text,
#                 response_id=response_id,
#                 response_text=answer,
#                 processing_time=(datetime.utcnow() - user_query.query_timestamp).total_seconds() if user_query.query_timestamp else None
#             )
#             logging_time = (datetime.utcnow() - start_logging).total_seconds()
#             logger.info(f"Query logged successfully, took {logging_time:.3f}s")
#         except Exception as e:
#             logger.error(f"Failed to log query to database: {str(e)}")
#             # Don't fail the request if logging fails

#         return response
#     else:
#         logger.warning("Selected text mode called without required selected_text parameter")
#         raise HTTPException(
#             status_code=400,
#             detail="Selected text mode requires selected_text parameter"
#         )


# @router.post("/chat-selected-text", response_model=ChatResponse)
# async def chat_with_selected_text(selected_text: str, query: str, session_id: str = None):
#     """Endpoint for asking questions about user-selected text only, bypassing full-book retrieval"""

#     # Validate inputs
#     if not selected_text or not selected_text.strip():
#         raise HTTPException(
#             status_code=400,
#             detail="selected_text cannot be empty"
#         )

#     if not query or not query.strip():
#         raise HTTPException(
#             status_code=400,
#             detail="query cannot be empty"
#         )

#     # Create a user query object for selected text mode
#     user_query = UserQuery(
#         query_id=str(uuid.uuid4()),
#         query_text=query,
#         selected_text=selected_text,
#         mode="selected_text",
#         session_id=session_id
#     )

#     # Log the selected text query
#     logger = logging.getLogger("rag_chatbot")
#     logger.info(f"Received selected-text query from session {session_id}")

#     # Call the shared logic for selected text
#     try:
#         response = chat_with_selected_text_endpoint(user_query)
#         logger.info(f"Selected-text response generated: {response.response_id}")
#         return response
#     except Exception as e:
#         logger.error(f"Error processing selected text query: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error processing selected text query: {str(e)}"
#         )


from fastapi import APIRouter, HTTPException
from src.models.entities import UserQuery, ChatResponse
from src.services.retrieval_service import retrieval_service
from src.services.book_service import book_service

from src.services.generation_service import generation_service
from src.services.database_service import database_service
import uuid
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger("rag_chatbot")

# =================================================================
# @router.post("/chat-test")
# async def chat_test():
#     return {"status": "ok", "message": "Backend reachable"}
# =================================================================



# @router.post("/chat", response_model=ChatResponse)
# async def chat_with_book(user_query: UserQuery):

#     if not user_query.query_text or not user_query.query_text.strip():
#         raise HTTPException(status_code=400, detail="query_text cannot be empty")

#     if not user_query.query_id:
#         user_query.query_id = str(uuid.uuid4())

#     if not user_query.query_timestamp:
#         user_query.query_timestamp = datetime.utcnow()

#     # 🔹 SELECTED TEXT MODE
#     if user_query.mode == "selected_text":
#         return await handle_selected_text(user_query)

#     # 🔹 FULL BOOK MODE
#     retrieved_chunks = await book_service.search_book_content(
#     book_id="book_content",
#     query_text=user_query.query_text,
#     top_k=5
# )


#     if retrieved_chunks:
#         answer = generation_service.generate_response(
#         query_text=user_query.query_text,
#         retrieved_chunks=retrieved_chunks
#     )

#         citations = [
#             {
#                 "chunk_id": c["chunk_id"],
#                 "book_id": c["book_id"],
#                 "chapter": c["chapter"],
#                 "section": c["section"],
#                 "paragraph_index": c["paragraph_index"]
#             }
#             for c in retrieved_chunks
#         ]

#     else:
#         answer = "This information is not available in the book."
#         citations = []

#     response_id = str(uuid.uuid4())

#     response = ChatResponse(
#         response_id=response_id,
#         query_id=user_query.query_id,
#         answer=answer,
#         citations=citations,
#         session_id=user_query.session_id,
#         is_fallback_response=not bool(citations),
#         based_on="full_book"
#     )

#     # 🔹 LOGGING (NON-BLOCKING)
#     try:
#         await database_service.log_query(
#             query_id=user_query.query_id,
#             query_text=user_query.query_text,
#             response_id=response_id,
#             response_text=answer,
#             processing_time=(datetime.utcnow() - user_query.query_timestamp).total_seconds()
#         )
#     except Exception:
#         logger.exception("DB logging failed")

#     return response


# # async def handle_selected_text(user_query: UserQuery):

#     if not user_query.selected_text:
#         raise HTTPException(
#             status_code=400,
#             detail="selected_text is required for selected_text mode"
#         )

#     context = "\n\n".join([c["content"] for c in retrieved_chunks])
#     # 🔹 chunks → context string

#     answer = generation_service.generate_response(
#         query_text=user_query.query_text,
#         context=context
#     )

#     response_id = str(uuid.uuid4())

#     response = ChatResponse(
#         response_id=response_id,
#         query_id=user_query.query_id,
#         answer=answer,
#         citations=[],
#         session_id=user_query.session_id,
#         is_fallback_response=False,
#         based_on="selected_text"
#     )

#     try:
#         await database_service.log_query(
#             query_id=user_query.query_id,
#             query_text=user_query.query_text,
#             response_id=response_id,
#             response_text=answer,
#             processing_time=(datetime.utcnow() - user_query.query_timestamp).total_seconds()
#         )
#     except Exception:
#         logger.exception("DB logging failed")

#     return response
# async def handle_selected_text(user_query: UserQuery):

#     if not user_query.selected_text:
#         raise HTTPException(
#             status_code=400,
#             detail="selected_text is required for selected_text mode"
#         )

#     answer = generation_service.generate_response(
#         query_text=user_query.query_text,
#         context=user_query.selected_text
#     )

#     response_id = str(uuid.uuid4())

#     response = ChatResponse(
#         response_id=response_id,
#         query_id=user_query.query_id,
#         answer=answer,
#         citations=[],
#         session_id=user_query.session_id,
#         is_fallback_response=False,
#         based_on="selected_text"
#     )

#     return response

@router.post("/chat", response_model=ChatResponse)
async def chat_with_book(user_query: UserQuery):

    if not user_query.query_text or not user_query.query_text.strip():
        raise HTTPException(status_code=400, detail="query_text cannot be empty")

    if not user_query.query_id:
        user_query.query_id = str(uuid.uuid4())

    if not user_query.query_timestamp:
        user_query.query_timestamp = datetime.utcnow()

    if user_query.mode == "selected_text":
        return await handle_selected_text(user_query)

    retrieved_chunks = retrieval_service.retrieve_relevant_chunks(
    query=user_query.query_text
)


    if retrieved_chunks:
        # context = "\n\n".join([c["content"] for c in retrieved_chunks])
        context = "\n\n".join([c.content for c in retrieved_chunks])
        print(f"[CHAT] Retrieved chunks count: {len(retrieved_chunks)}")


        # context = "\n\n".join([c["content"] for c in retrieved_chunks])

        answer = await generation_service.generate_response(
        query_text=user_query.query_text,
        context=context
    )
        print(f"[CHAT] Context length: {len(context)}")




        citations = [
            {
                "chunk_id": c.chunk_id,
                "book_id": c.book_id,
                "chapter": c.chapter,
                "section": c.section,
                "paragraph_index": c.paragraph_index
            }
            for c in retrieved_chunks
        ]

    else:
        answer = "This information is not available in the book."
        citations = []

    return ChatResponse(
        response_id=str(uuid.uuid4()),
        query_id=user_query.query_id,
        answer=answer,
        citations=citations,
        session_id=user_query.session_id,
        is_fallback_response=not bool(citations),
        based_on="full_book"
    )

async def handle_selected_text(user_query: UserQuery):

    if not user_query.selected_text:
        raise HTTPException(
            status_code=400,
            detail="selected_text is required"
        )

    answer = generation_service.generate_response(
        query_text=user_query.query_text,
        context=user_query.selected_text
    )

    return ChatResponse(
        response_id=str(uuid.uuid4()),
        query_id=user_query.query_id,
        answer=answer,
        citations=[],
        session_id=user_query.session_id,
        is_fallback_response=False,
        based_on="selected_text"
    )
