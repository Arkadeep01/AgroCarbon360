# AgroCarbon360 Backend

FastAPI backend for the AgroCarbon360 carbon MRV (Measurement, Reporting, and Verification) platform.

## Features

- FastAPI REST API
- SQLAlchemy ORM with SQLite/PostgreSQL support
- JWT Authentication
- Role-based access control
- CORS support for frontend integration

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python start.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Environment Variables

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `ALLOWED_ORIGINS`: CORS allowed origins

## Docker

Build and run with Docker:

```bash
docker build -t agrocarbon360-backend .
docker run -p 8000:8000 agrocarbon360-backend
```

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── start.py             # Development server script
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── src/
│   ├── auth/           # Authentication module
│   ├── db/             # Database configuration
│   ├── farmer/         # Farmer-related APIs
│   ├── fpo/            # FPO-related APIs
│   ├── carbon_engine/  # Carbon calculation engine
│   ├── blockchain/     # Blockchain integration
│   ├── verification/   # Verification services
│   └── utils/          # Utility functions
└── tests/              # Test files
```
