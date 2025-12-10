# Quickstart: Textbook Generation

## Prerequisites
- Python 3.11+
- Node.js 18+
- Access to AI model API (e.g., OpenAI API key)
- PostgreSQL database

## Setup

### 1. Environment Configuration
```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Environment Variables
Create a `.env` file in the backend directory:
```bash
# Backend environment variables
DATABASE_URL=postgresql://username:password@localhost/textbook_db
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
DEBUG=False
```

### 3. Database Setup
```bash
# Run database migrations
cd backend
python -m alembic upgrade head
```

### 4. Start Services
```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn src.api.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm start
```

## API Endpoints

### Textbook Generation
- `POST /api/v1/textbook/generate` - Generate a new textbook
- `GET /api/v1/textbook/{id}` - Get textbook details
- `PUT /api/v1/textbook/{id}/review` - Update textbook after review
- `POST /api/v1/textbook/{id}/export` - Export textbook in specified format

### Content Management
- `GET /api/v1/textbook/{textbook_id}/chapters` - List chapters
- `PUT /api/v1/chapter/{id}` - Update chapter content
- `PUT /api/v1/section/{id}` - Update section content

## Usage Example

### Generate a Textbook
```bash
curl -X POST http://localhost:8000/api/v1/textbook/generate \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Introduction to Computer Science",
    "educational_level": "UNDERGRADUATE",
    "title": "CS101 Textbook",
    "settings": {
      "include_exercises": true,
      "include_summaries": true,
      "output_format": "PDF"
    }
  }'
```

### Review and Edit Content
1. Access the frontend interface at `http://localhost:3000`
2. View the generated textbook
3. Edit any chapter or section as needed
4. Save changes which will update the backend

## Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## Deployment
1. Set `DEBUG=False` in environment
2. Configure production database
3. Build frontend: `npm run build`
4. Deploy backend with production WSGI server