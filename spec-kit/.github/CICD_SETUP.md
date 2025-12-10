# CI/CD Setup

This document explains the Continuous Integration and Continuous Deployment setup for the Textbook Generation application.

## Overview

The CI/CD pipeline is configured using GitHub Actions and consists of:

1. **CI Pipeline** - Runs on every push and pull request
2. **Staging CD Pipeline** - Runs on pushes to the `develop` branch
3. **Production CD Pipeline** - Runs on pushes to the `main` branch

## CI Pipeline (.github/workflows/ci.yml)

The CI pipeline performs the following checks:

### Backend Tests
- Sets up Python 3.11 environment
- Installs dependencies from requirements.txt
- Runs all backend tests using pytest
- Performs linting with flake8

### Frontend Tests
- Sets up Node.js 18 environment
- Installs dependencies from package-lock.json
- Runs frontend tests with coverage
- Builds the frontend application

## CD Pipelines

### Staging Deployment (.github/workflows/cd-staging.yml)
- Triggered on pushes to the `develop` branch
- Deploys to the staging environment
- Builds and pushes Docker images to Docker Hub
- Deploys both backend and frontend

### Production Deployment (.github/workflows/cd-production.yml)
- Triggered on pushes to the `main` branch
- Deploys to the production environment
- Requires 80% test coverage for both backend and frontend
- Builds and pushes Docker images to Docker Hub
- Deploys both backend and frontend with production configurations

## Required Secrets

The following secrets need to be configured in GitHub repository settings:

### For Docker
- `DOCKERHUB_USERNAME` - Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token

### For Frontend Production
- `REACT_APP_API_BASE_URL` - Production API base URL

## Docker Configuration

Both backend and frontend have Dockerfiles for containerization:

- `backend/Dockerfile` - For the FastAPI backend
- `frontend/Dockerfile` - For the React frontend

## Environments

The pipeline uses GitHub Environments for deployment:
- `staging` environment for staging deployments
- `production` environment for production deployments

These environments can have protection rules and secrets configured separately in GitHub.

## Branch Strategy

- `main` branch: Production code, triggers production deployment
- `develop` branch: Staging code, triggers staging deployment
- `feature/**` branches: Development features, triggers CI checks only