# dise-api

**Car Rental API** built with FastAPI.

A modern backend service for managing car rentals, users, and bookings.  
Currently includes user authentication. Vehicle management, booking system, and more features are planned.

---

## Overview

`dise-api` is a RESTful API designed for a car rental platform.  
It allows users to register, log in, and (in future versions) browse available cars, make bookings, and manage rentals.

### Current Focus
- Secure user authentication (JWT)
- Database migrations with Alembic
- Clean and scalable project structure

### Planned Features
- Vehicle listing & management
- Car availability & booking system
- Rental history
- Admin dashboard endpoints
- Payment integration (future)

---

## Features

- [x] User registration
- [x] User login (JWT)
- [x] Password hashing (Argon2)
- [x] Database migrations (Alembic)
- [ ] Vehicle management (CRUD)
- [ ] Car availability checking
- [ ] Booking / Rental system
- [ ] Role-based access (User / Admin)
- [ ] Refresh tokens
- [ ] User profile management
- [ ] Password reset & email verification

---

## Tech Stack

| Layer            | Technology              |
|------------------|-------------------------|
| Framework        | FastAPI                 |
| Language         | Python 3.12+            |
| ORM              | SQLAlchemy 2.x          |
| Migrations       | Alembic                 |
| Validation       | Pydantic v2             |
| Auth             | JWT + pwdlib (Argon2)   |
| Database         | PostgreSQL              |
| ASGI Server      | Uvicorn                 |

---

## Project Structure

```text
dise-api/
├── alembic/                  # Database migrations
├── app/
│   ├── api/                  # API routes
│   │   └── auth.py
│   ├── core/                 # Config & settings
│   ├── db/                   # Database session
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   ├── utils/                # Helpers & enums
│   └── main.py               # Application entrypoint
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python **3.12+**
- PostgreSQL
- Git

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd dise-api
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://diseuser:yourpassword@localhost:5432/dise_api
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> Generate a strong secret key:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## Database Setup

### 1. Create PostgreSQL user and database

```bash
sudo -u postgres psql
```

```sql
CREATE USER diseuser WITH PASSWORD 'yourpassword';
CREATE DATABASE dise_api OWNER diseuser;
GRANT ALL PRIVILEGES ON DATABASE dise_api TO diseuser;
\q
```

### 2. Run migrations

```bash
alembic upgrade head
```

### 3. Create new migration (after model changes)

```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### Useful Alembic commands

```bash
alembic current          # Check current version
alembic history          # Show migration history
alembic downgrade -1     # Rollback one step
```

---

## Running the Application

### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
fastapi dev app/main.py
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Documentation

Once the server is running:

| Resource       | URL                              |
|----------------|----------------------------------|
| Swagger UI     | http://127.0.0.1:8000/docs       |
| ReDoc          | http://127.0.0.1:8000/redoc      |
| OpenAPI JSON   | http://127.0.0.1:8000/openapi.json |

---

## Available Endpoints (Current)

| Method | Endpoint           | Description              |
|--------|--------------------|--------------------------|
| `POST` | `/auth/register`   | Create a new user        |
| `POST` | `/auth/login`      | Login and get JWT token  |

---

## Roadmap

- [ ] Vehicle management (add, update, delete cars)
- [ ] Car availability & search filters
- [ ] Booking / rental system
- [ ] Role-based access control (Admin / User)
- [ ] Refresh token support
- [ ] User profile & rental history
- [ ] Email verification & password reset
- [ ] Rate limiting & better logging
- [ ] Unit & integration tests

---

## License

MIT
