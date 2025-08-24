# tenders.uz

A minimal FastAPI application for user management and workspace functionality in a tender/bidding platform.

## Features

✅ **User Authentication**
- User registration with email validation
- JWT-based login/logout system
- Secure password hashing with bcrypt

✅ **Balance Management**
- Top-up balance functionality
- Balance tracking for each user

✅ **Payment Information**
- Update and store payment details (JSON format)
- Secure storage and validation

✅ **Workspace Management**
- Create public or private workspaces
- Access control (only owners can modify private workspaces)
- Public workspace discovery
- Full CRUD operations for workspace owners

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. Access the API:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Documentation

See [API_DOCS.md](API_DOCS.md) for detailed API documentation and usage examples.

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database (easily replaceable)
- **JWT** - Secure token-based authentication
- **Pydantic** - Data validation using Python type annotations
- **bcrypt** - Password hashing

## Project Structure

```
├── main.py           # FastAPI application and routes
├── database.py       # Database models and connection
├── schemas.py        # Pydantic models for request/response
├── auth.py          # Authentication and authorization logic
├── config.py        # Application configuration
├── requirements.txt # Python dependencies
├── .env            # Environment variables (not in git)
├── .gitignore      # Git ignore rules
└── API_DOCS.md     # Detailed API documentation
```