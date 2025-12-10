# Deployment Documentation for Unified Physical AI & Humanoid Robotics Learning Book

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Deployment Methods](#deployment-methods)
5. [Configuration](#configuration)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Overview
This document provides instructions for deploying the Unified Physical AI & Humanoid Robotics Learning Book application. The application consists of a FastAPI backend, Docusaurus frontend, PostgreSQL database, and Qdrant vector database for RAG functionality.

## Prerequisites
- Docker and Docker Compose
- Git
- Python 3.9+ (for local development)
- Node.js 16+ (for local development)
- Access to OpenAI API key
- Access to Qdrant Cloud (or self-hosted Qdrant instance)

## Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/unified-book-project.git
cd unified-book-project
```

### 2. Set up Environment Variables
Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/unified_book
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=unified_book

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key

# API Keys
OPENAI_API_KEY=your_openai_api_key

# Security
SECRET_KEY=your_very_long_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
FRONTEND_URL=http://localhost:3000
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### 3. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Deployment Methods

### Method 1: Docker Compose (Recommended for Production)

#### 1. Build and Start Services
```bash
cd backend
docker-compose up --build -d
```

#### 2. Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

#### 3. Import Initial Data (if needed)
```bash
docker-compose exec backend python init_db.py
```

### Method 2: Manual Deployment

#### Backend Deployment
1. Set up Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the application:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Deployment for GitHub Pages
1. Build the Docusaurus site:
```bash
npm run build
```

2. Deploy to GitHub Pages using the gh-pages branch:
```bash
npm run deploy
```

## Configuration

### Database Configuration
The application uses PostgreSQL for storing user data, chapters, and other structured information. Ensure your PostgreSQL instance is properly configured with adequate storage and backup strategies.

### Qdrant Configuration
The RAG system uses Qdrant for vector storage. Ensure your Qdrant instance has sufficient memory and storage for embedding vectors. The default configuration uses a 1536-dimensional vector space for OpenAI embeddings.

### Environment Variables
Key environment variables for production deployment:

- `DATABASE_URL`: PostgreSQL connection string
- `QDRANT_URL`: Qdrant instance URL
- `OPENAI_API_KEY`: OpenAI API key for embeddings and completions
- `SECRET_KEY`: JWT secret key (should be a long, random string)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `ENVIRONMENT`: Set to "production" to enable production optimizations

## Monitoring and Maintenance

### Health Checks
The application provides health check endpoints:
- Backend: `GET /health`
- Frontend: `GET /` (should return 200)

### Logging
Application logs are stored in the `logs/` directory. Configure log rotation to prevent disk space issues.

### Backup Strategy
1. PostgreSQL database backup:
```bash
pg_dump unified_book > backup.sql
```

2. Qdrant backup: Follow Qdrant's backup procedures for your deployment method.

### Performance Monitoring
Monitor these key metrics:
- API response times (target: <500ms p95)
- Database connection pool usage
- Qdrant vector search performance
- Memory and CPU usage

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
- Verify PostgreSQL is running and accessible
- Check database credentials in environment variables
- Ensure database migrations have been run

#### 2. Qdrant Connection Issues
- Verify Qdrant instance is running
- Check Qdrant URL and API key in environment variables
- Ensure network connectivity between services

#### 3. Frontend Build Issues
- Verify Node.js version is compatible (16+)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

#### 4. OpenAI API Issues
- Verify API key is valid and has sufficient quota
- Check OpenAI service status
- Verify network connectivity to OpenAI endpoints

### Debugging Production Issues
1. Check application logs in the `logs/` directory
2. Use Docker logs for containerized deployments:
```bash
docker-compose logs backend
docker-compose logs db
```
3. Verify environment variables are correctly set
4. Test individual service connectivity

## Scaling Recommendations

### Horizontal Scaling
- Use a load balancer for multiple backend instances
- Implement Redis for session management across instances
- Use a managed PostgreSQL service for better scaling

### Performance Optimization
- Implement caching strategies for frequently accessed content
- Optimize database queries with proper indexing
- Use CDN for static assets

## Security Considerations

### API Security
- Use HTTPS in production
- Implement rate limiting
- Validate and sanitize all user inputs
- Use parameterized queries to prevent SQL injection

### Data Security
- Encrypt sensitive data at rest
- Use secure token storage
- Implement proper authentication and authorization
- Regular security audits and dependency updates

---

For support or questions about deployment, please contact the development team or refer to the project's issue tracker.