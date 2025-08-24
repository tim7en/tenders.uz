# Tenders.uz API

A minimal FastAPI application that provides user management and workspace functionality for a tender/bidding platform.

## Features

- User registration and authentication
- JWT-based login/logout system
- Balance management (top-up functionality)
- Payment information management
- Workspace creation and management (public/private)
- User access control for workspaces

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables by copying `.env.example` to `.env` and updating values:
```bash
cp .env .env.local  # and edit as needed
```

3. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`

## API Endpoints

### Authentication

- `POST /register` - Register a new user
- `POST /token` - Login and get access token

### User Management

- `GET /users/me` - Get current user information
- `POST /users/top-up-balance` - Add funds to user balance
- `PUT /users/payment-info` - Update payment information

### Workspaces

- `POST /workspaces` - Create a new workspace
- `GET /workspaces/my` - Get user's workspaces
- `GET /workspaces/public` - Get all public workspaces
- `GET /workspaces/{id}` - Get specific workspace (if public or owned by user)
- `PUT /workspaces/{id}` - Update workspace (owner only)
- `DELETE /workspaces/{id}` - Delete workspace (owner only)

## Example Usage

### 1. Register a user
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### 2. Login and get token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 3. Use token for authenticated requests
```bash
TOKEN="your-token-here"
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Top up balance
```bash
curl -X POST "http://localhost:8000/users/top-up-balance" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0}'
```

### 5. Create a workspace
```bash
curl -X POST "http://localhost:8000/workspaces" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Workspace", "description": "A test workspace", "is_public": true}'
```

## Data Models

### User
- `id`: Unique identifier
- `username`: Unique username
- `email`: Unique email address
- `balance`: User's account balance
- `payment_info`: JSON string containing payment details
- `is_active`: Account status
- `created_at`: Registration timestamp

### Workspace
- `id`: Unique identifier
- `name`: Workspace name
- `description`: Optional description
- `is_public`: Public/private visibility
- `owner_id`: ID of the user who owns the workspace
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Access control for private workspaces
- Input validation and sanitization

## Configuration

Environment variables:
- `SECRET_KEY`: JWT signing key (change in production!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `DATABASE_URL`: Database connection string (default: SQLite)