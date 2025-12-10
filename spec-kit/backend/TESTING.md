# Testing Setup

This document explains how to run tests for the Textbook Generation API.

## Backend Testing

### Running Tests

To run all tests:
```bash
cd backend
python -m pytest
```

To run unit tests only:
```bash
cd backend
python -m pytest tests/unit/
```

To run integration tests only:
```bash
cd backend
python -m pytest tests/integration/
```

To run contract tests only:
```bash
cd backend
python -m pytest tests/contract/
```

### Test Coverage

To run tests with coverage report:
```bash
cd backend
python -m pytest --cov=src --cov-report=html
```

The coverage report will be generated in the `htmlcov/` directory.

### Adding New Tests

- Place unit tests in `tests/unit/` directory
- Place integration tests in `tests/integration/` directory
- Place contract tests in `tests/contract/` directory
- Name test files with the prefix `test_` or suffix `_test`
- Use pytest fixtures from `conftest.py` when needed

## Frontend Testing

Frontend tests are run using Jest through react-scripts:

To run all frontend tests:
```bash
cd frontend
npm test
```

To run tests in watch mode:
```bash
cd frontend
npm test -- --watch
```

## Test Structure

### Backend Test Structure
- `tests/unit/` - Unit tests for individual functions and classes
- `tests/integration/` - Integration tests for API endpoints and service interactions
- `tests/contract/` - Contract tests to verify API contracts

### Frontend Test Structure
- `*.test.tsx` - Component tests using React Testing Library
- `*.test.ts` - Service and utility function tests

## Test Configuration

- Backend tests use an in-memory SQLite database
- Frontend tests use the built-in Jest configuration from Create React App
- Both test suites follow AAA (Arrange, Act, Assert) pattern
- Tests are organized by feature and type for maintainability