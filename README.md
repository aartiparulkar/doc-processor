# Document Processing Backend

A backend service for uploading, managing, and processing documents.

This project is being built as a production-oriented FastAPI application while learning backend engineering fundamentals such as 
HTTP APIs, validation, PostgreSQL, authentication, background processing, testing, Docker, and observability.

## Current Status

Currently implemented:

- FastAPI application setup
- `GET /health` endpoint
- Project structure using a `src/` layout
- User Registration and authentication (`POST /register`, `POST /login` endpoints)
- Documents: CRUD APIs, Extract PDF, View Status (`POST /upload`, `GET /{document_id}`, `POST /upload`, `GET /{document_id}/status`, `DELETE /{document_id}` endpoints)

The project is being developed incrementally.

## Planned Features

The project will include:

- Document CRUD APIs
- Pydantic request and response validation
- Predictable API error handling
- PostgreSQL persistence
- User registration and authentication
- User-scoped document access
- PDF upload and validation
- Background document processing
- Processing job status tracking
- Automated tests
- Docker-based local environment
- Structured logging
- Health and readiness endpoints
- Basic performance benchmarks

## Tech Stack

- Python 3.12+
- FastAPI
- Pydantic
- PostgreSQL
- SQLAlchemy
- Alembic
- pytest
- Docker

## Project Structure

```text
document-processing-backend/
├── src/
│   └── doc_processor/
│       ├── api/
│       ├── core/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── repositories/
│       ├── db/
│       └── main.py
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Run Locally

Install dependencies:

```bash
uv sync
```

Start the API:

```bash
uv run uvicorn doc_processor.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

## Project Goal

The goal is not only to build a working API, but to understand the engineering decisions behind it: API contracts, validation, persistence, authentication, asynchronous processing, testing, reliability, and performance.
