Here's a clean, professional **README.md** for your **dise-api** project:

```markdown
# dise-api

Modern FastAPI backend with user authentication.  
Currently supports user registration & login. More features (roles, refresh tokens, profile management, etc.) are planned.

---

## Features

- [x] User registration
- [x] User login (JWT)
- [x] Password hashing
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
| ORM              | SQLAlchemy              |
| Migrations       | Alembic                 |
| Validation       | Pydantic v2             |
| Auth             | JWT + Passlib           |
| Database         | PostgreSQL (recommended)|
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
└── README.md
```

---

## Prerequisites

- Python **3.12+**
- PostgreSQL (or SQLite for quick testing)
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
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If you don't have a `requirements.txt` yet, install the core packages:

```bash
pip install "fastapi[standard]" sqlalchemy alembic pydantic-settings python-jose[cryptography] passlib[bcrypt] psycopg2-binary
```

### 4. Environment variables

Create a `.env` file in the project root:

```env
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/dise_api
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **Important:** Never commit the real `.env` file.

### 5. Database setup

```bash
# Run migrations
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

Once the server is running, open:

| Resource              | URL                              |
|-----------------------|----------------------------------|
| Swagger UI            | http://127.0.0.1:8000/docs       |
| ReDoc                 | http://127.0.0.1:8000/redoc      |
| OpenAPI JSON          | http://127.0.0.1:8000/openapi.json |

---

## Docker (optional)

```bash
docker-compose up --build
```

---

## Available Auth Endpoints

| Method | Endpoint           | Description              |
|--------|--------------------|--------------------------|
| `POST` | `/auth/register`   | Create a new user        |
| `POST` | `/auth/login`      | Login and get JWT token  |

> Exact paths may vary depending on how the router is mounted in `main.py`.

---

## Development Tips

- Always create a new Alembic migration after changing models:
  ```bash
  alembic revision --autogenerate -m "description of changes"
  alembic upgrade head
  ```
- Use `--reload` only in development.
- Keep secrets in `.env` and load them via `pydantic-settings`.

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
```

---

### Quick tips for you

1. Replace `<your-repo-url>` with your actual GitHub/GitLab URL.
2. Adjust the endpoint paths (`/auth/register`, `/auth/login`) if your actual routes are different.
3. Add a real `requirements.txt` if you don’t have one yet (I can generate one for you if you want).
4. If you use Docker, make sure your `docker-compose.yml` matches the services you actually have.

