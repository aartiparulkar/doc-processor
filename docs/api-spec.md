# API Specification

## Authentication

### `POST /auth/register`

Create a new user.

**Request body**

```json
{
  "email": "aarti@example.com",
  "password": "some-password"
}
```

### `POST /auth/login`

Authenticate an existing user.

**Request body**

```json
{
  "email": "aarti@example.com",
  "password": "some-password"
}
```

## Documents

### `POST /documents`

Upload a document for processing.

### `GET /documents`

Return documents belonging to the authenticated user.

**Response**

```json
{
  "documents": [
    {
      "id": "doc_123",
      "filename": "1985_letter.pdf",
      "year": 1985,
      "status": "completed"
    }
  ]
}
```

### `GET /documents/{document_id}`

Get information about a document.

### `DELETE /documents/{document_id}`

Delete a document.

## Processing

### `GET /documents/{document_id}/status`

Check whether a document has finished processing.

**Response**

```json
{
  "document_id": "doc_123",
  "status": "processing"
}
```

## Content

### `GET /documents/{document_id}/text`

Retrieve the text extracted from a document.

## System

### `GET /health`

Check whether the backend application is alive.
