# API Server

Simple RESTful API with JWT authentication, designed to demonstrate secure API interactions.

## Installation

```bash
cd packages/api-server
npm install
```

## Run Server

```bash
npm start
```

Server will run on `http://localhost:3006`

## API Endpoints

### 1. GET /generate-token
Generate a temporary JWT token for testing purposes.

**Response:**
```json
{
  "message": "Token generated successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR...",
  "expiresIn": "8h"
}
```

**Example:**
```bash
curl -X GET "http://localhost:3006/generate-token"
```

### 2. GET /get_email/:account_id
Get email by account ID.

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>`
- `x-cdl-tenant-id: test123`

**Path Parameters:**
- `account_id` (required): 5-10 digits

**Example:**
```bash
curl -X GET "http://localhost:3006/get_email/12345" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "x-cdl-tenant-id: test123"
```

### 3. POST /change_email
Change email for an account.

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>`
- `x-cdl-tenant-id: test123`
- `Content-Type: application/json`

**Body Parameters:**
- `account_id` (required): 5-10 digits
- `new_email` (required): valid email address

**Example:**
```bash
curl -X POST "http://localhost:3006/change_email" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "x-cdl-tenant-id: test123" \
  -H "Content-Type: application/json" \
  -d '{"account_id":"12345","new_email":"newemail@example.com"}'
```

## Authentication & Security

- **JWT Authentication**: All protected endpoints require a valid Bearer token in the `Authorization` header.
- **Tenant Verification**: All protected endpoints require the `x-cdl-tenant-id` header to be set to `test123`.
- **Validation**:
  - `account_id`: Must be a string of 5 to 10 digits.
  - `email`: Must be a valid email format.

## Response Codes

- `200`: Success
- `400`: Bad request (invalid or missing parameters)
- `401`: Unauthorized (missing token)
- `403`: Forbidden (invalid token or tenant ID)
