# LabAssist Backend

AI-powered lab report analytics backend built with FastAPI and MongoDB.

## Project Structure

```
backend/
├── api.py              # Main FastAPI application
├── api_v2.py           # V2 API endpoints
├── main.py             # CLI entry point
├── requirements.txt    # Python dependencies
├── config/            # Configuration modules
│   ├── canonical_mappings.py
│   ├── canonical_mappings_v2.py
│   ├── unit_mappings.py
│   ├── reference_ranges.py
│   └── thresholds.py
├── db/                # Database models
│   └── models.py
├── modules/           # Core modules
│   ├── ai_parser.py
│   ├── ai_parser_v2.py
│   ├── ingestion.py
│   ├── ingestion_v2.py
│   ├── query_builder_v2.py
│   ├── query_executor.py
│   ├── query_schema_v2.py
│   └── response_generator.py
├── images/            # Sample lab report images
└── static/            # Static assets (legacy HTML UI)
```

## Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Create a `.env` file:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   DATABASE_NAME=lab_assistant
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Start MongoDB**
   ```bash
   # Make sure MongoDB is running locally
   mongod
   ```

## Running the API

### Development Server
```bash
uvicorn api:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

### API Documentation
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## API Endpoints

### Health Check
```
GET /health
```

### Query Natural Language
```
POST /api/query
Body: { "query": "Show patients with low hemoglobin" }
```

### Get Statistics
```
GET /api/stats
```

### Get Recent Abnormal Results
```
GET /api/recent-abnormal?limit=10
```

### Get All Patients
```
GET /api/patients
```

### Ingest Lab Report
```
POST /api/ingest
Body: { "file_path": "path/to/report.json" }
```

## Testing

Run test files:
```bash
python test_api.py
python test_query.py
python test_ingestion.py
```

## Database

The application uses MongoDB with the following collections:
- `lab_tests` - Normalized lab test results
- `queries` - Query logs and analytics

## Features

- ✅ Natural language query processing
- ✅ Canonical test name normalization
- ✅ Unit conversion and normalization
- ✅ Reference range validation
- ✅ Abnormal result detection
- ✅ Patient analytics and trends
- ✅ AI-powered query parsing (Groq LLM)

## Tech Stack

- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **Groq** - LLM API for query parsing
- **Pydantic** - Data validation
