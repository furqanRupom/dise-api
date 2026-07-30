# dise-api

Modern FastAPI backend with user authentication.  
Currently supports user registration & login. More features (roles, refresh tokens, profile management, etc.) are planned.

---

## Features

- [x] User registration
- [x] User login (JWT)
- [x] Password hashing (Argon2)
- [x] Database migrations (Alembic)
- [ ] Refresh tokens
- [ ] Role-based access control
- [ ] User profile endpoints
- [ ] Password reset / email verification

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
# Apply all existing migrations
alembic upgrade head
```

### 3. (Optional) Create a new migration after changing models

```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### Useful Alembic commands

```bash
# Check current migration version
alembic current

# Show migration history
alembic history

# Downgrade one step
alembic downgrade -1

# Reset database (drop all tables and re-apply)
alembic downgrade base
alembic upgrade head
```

---

## Running the Application

### Development (recommended)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using the FastAPI CLI:

```bash
fastapi dev app/main.py
```

### Production style

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

## Available Auth Endpoints

| Method | Endpoint           | Description              |
|--------|--------------------|--------------------------|
| `POST` | `/auth/register`   | Create a new user        |
| `POST` | `/auth/login`      | Login and get JWT token  |

---

## Docker (optional)

```bash
docker-compose up --build
```

---

## Development Tips

- Always create a new Alembic migration after changing models.
- Use `--reload` only in development.
- Never commit the real `.env` file.
- Keep secrets in `.env` and load them with `pydantic-settings`.

---

## Roadmap

- [ ] Refresh token support
- [ ] Role-based permissions (admin / user)
- [ ] User profile management
- [ ] Email verification & password reset
- [ ] Rate limiting
- [ ] Better error handling & logging
- [ ] Unit & integration tests

---

## License

MIT
