# Railway Deployment

This FastAPI backend can be deployed to Railway with the following configuration:

## Environment Variables Required

- `ENVIRONMENT`: Set to "railway" for Railway deployment
- `DATABASE_URL`: PostgreSQL database URL (can use Railway's PostgreSQL addon)
- `SECRET_KEY`: Secret key for JWT tokens
- `COHERE_API_KEY`: Cohere API key for embeddings
- `QDRANT_URL`: Qdrant vector database URL (can be cloud or self-hosted)
- `QDRANT_API_KEY`: Qdrant API key
- `CCR_QWEN_TOKEN`: CCR Qwen token for AI responses
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (e.g., "https://your-frontend.com,https://*.railway.app")

## Deployment Steps

1. Connect your GitHub repository to Railway
2. Select this directory (`spec-kit/backend`) for deployment
3. Railway will automatically detect this as a Python application
4. Add the required environment variables
5. Deploy!

## Health Check

The application exposes a health check endpoint at `/health` which returns `{"status": "healthy"}` when the service is running properly.

## RAG Endpoints

The deployed backend includes full RAG functionality:
- `/api/v1/ingest` - Ingest documents into the vector database
- `/api/v1/query` - Query the RAG system
- `/api/v1/session` - Create chat sessions
- `/api/v1/session/{session_id}/message` - Add messages to sessions
- `/api/v1/sources/{hit_id}` - Get source content by hit ID
- `/api/v1/admin/reindex` - Admin endpoint to reindex all documents
- `/api/v1/admin/collections` - Admin endpoint to get collections info

## Notes

- The application uses uvicorn to serve on the PORT environment variable as required by Railway
- Database migrations are handled automatically during deployment
- Qdrant is used for vector storage with Cohere embeddings