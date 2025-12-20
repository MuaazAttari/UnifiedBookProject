# API Contract: Integrated RAG Chatbot

## Base URL
`/api/v1`

## Endpoints

### 1. Chat with Book Content
`POST /chat`

#### Description
Main endpoint for asking questions about book content with full-book retrieval

#### Request
```json
{
  "query": "string (the question to ask)",
  "session_id": "string (optional, for conversation tracking)"
}
```

#### Response (Success)
```json
{
  "response_id": "string",
  "answer": "string (the answer based on book content)",
  "citations": [
    {
      "chunk_id": "string",
      "book_id": "string",
      "chapter": "string",
      "section": "string",
      "paragraph_index": "integer"
    }
  ],
  "query_id": "string",
  "session_id": "string"
}
```

#### Response (No Content Found)
```json
{
  "response_id": "string",
  "answer": "This information is not available in the book.",
  "citations": [],
  "query_id": "string",
  "session_id": "string"
}
```

#### Error Response
```json
{
  "error": "string (error description)",
  "error_code": "string"
}
```

### 2. Chat with Selected Text Only
`POST /chat-selected-text`

#### Description
Endpoint for asking questions about user-selected text only, bypassing full-book retrieval

#### Request
```json
{
  "selected_text": "string (the text selected by user)",
  "query": "string (the question about the selected text)",
  "session_id": "string (optional, for conversation tracking)"
}
```

#### Response
```json
{
  "response_id": "string",
  "answer": "string (the answer based only on selected text)",
  "based_on": "selected_text",
  "query_id": "string",
  "session_id": "string"
}
```

### 3. Health Check
`GET /health`

#### Description
Health check endpoint for service monitoring

#### Response
```json
{
  "status": "healthy",
  "timestamp": "datetime (ISO 8601)"
}
```

### 4. Book Metadata
`GET /books/{book_id}`

#### Description
Retrieve metadata about a specific book

#### Response
```json
{
  "book_id": "string",
  "title": "string",
  "author": "string",
  "chapters_count": "integer",
  "indexed": "boolean",
  "last_indexed": "datetime (ISO 8601)"
}
```