# Data Model: Integrated RAG Chatbot

## Entities

### BookContent
- **book_id** (string): Unique identifier for the book
- **chapter** (string): Chapter name or identifier
- **section** (string): Section name or identifier  
- **paragraph_index** (integer): Sequential index of paragraph within section
- **page_number** (integer): Physical or logical page number
- **content_type** (string): Type of content (text, code, figure, etc.)
- **content** (text): The actual text content
- **chunk_id** (string): Unique identifier for this content chunk
- **embedding_vector** (array): Vector representation of the content (stored separately in vector DB)

### RetrievedChunk
- **chunk_id** (string): Reference to the original BookContent chunk
- **book_id** (string): Book identifier
- **chapter** (string): Chapter name
- **section** (string): Section name
- **paragraph_index** (integer): Paragraph index within section
- **content** (text): The actual text content of the chunk
- **relevance_score** (float): Similarity score from vector search
- **metadata** (object): Additional metadata from original content

### UserQuery
- **query_id** (string): Unique identifier for the query
- **user_id** (string): Identifier for the user (optional, for tracking)
- **query_text** (text): The original question/query from user
- **query_timestamp** (datetime): When the query was submitted
- **selected_text** (text): If in selected text mode, the user-provided text
- **mode** (enum): Query mode - "full_book" or "selected_text"
- **session_id** (string): Identifier for the conversation session

### ChatResponse
- **response_id** (string): Unique identifier for the response
- **query_id** (string): Reference to the original query
- **response_text** (text): The generated response text
- **generation_timestamp** (datetime): When the response was generated
- **retrieved_chunks** (array): List of chunk_ids used to generate the response
- **source_citations** (array): Citations to source content
- **is_fallback_response** (boolean): Whether this is a fallback "not available" response

### QueryLog
- **log_id** (string): Unique identifier for the log entry
- **query_id** (string): Reference to the original query
- **query_text** (text): The original question
- **response_id** (string): Reference to the response
- **response_text** (text): The response given
- **processing_time** (float): Time in seconds to process the query
- **user_feedback** (string): Optional user feedback
- **log_timestamp** (datetime): When the log was created