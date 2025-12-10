# Environment Configuration

This document explains how to set up and manage different environments for the Textbook Generation API.

## Environment Types

The application supports three environments:

1. **Local** - For development on your local machine
2. **Staging** - For testing in a production-like environment
3. **Production** - For the live application

## Environment Variables

| Variable | Description | Local | Staging | Production |
|----------|-------------|-------|---------|------------|
| ENVIRONMENT | Specifies the environment | local | staging | production |
| DATABASE_URL | Database connection string | localhost | staging DB | production DB |
| SECRET_KEY | Secret key for JWT tokens | dev key | staging key | production key |
| ALGORITHM | JWT algorithm | HS256 | HS256 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 | 30 | 30 |
| OPENAI_API_KEY | API key for OpenAI integration | local key | staging key | production key |
| DEBUG | Enable/disable debug mode | True | True | False |
| ALLOWED_ORIGINS | Comma-separated list of allowed origins | localhost | staging domain | production domains |

## Setup Instructions

### Local Environment
1. Copy `.env.example` to `.env`
2. Update the values as needed for your local setup
3. Run the application normally

### Staging Environment
1. Copy `.env.staging` to `.env`
2. Update the values with staging-specific configurations
3. Deploy to staging environment

### Production Environment
1. Copy `.env.prod` to `.env`
2. Update the values with production-specific configurations
3. Deploy to production environment

## Docker Support

If using Docker, you can specify the environment file using:

```bash
docker run -e ENVIRONMENT=production your-image
```

## Configuration Loading Priority

The application loads configuration in the following order:

1. Default values in the Settings class
2. Values from environment variables
3. Values from the .env file

This allows for flexible configuration in different deployment scenarios.