# dise-api

A FastAPI backend for a car rental platform. Handles user authentication today; vehicle listings, bookings, and rental management are next.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## Status

| Feature | Status |
|---|---|
| User registration & login (JWT) | ✅ Done |
| Password hashing (Argon2) | ✅ Done |
| Database migrations (Alembic) | ✅ Done |
| Vehicle management | 🚧 Planned |
| Booking / rental system | 🚧 Planned |
| Role-based access | 🚧 Planned |
| Refresh tokens | 🚧 Planned |
| Password reset / email verification | 🚧 Planned |

## Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.12+
- **Database:** PostgreSQL, via SQLAlchemy 2.x
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Auth:** JWT + Argon2 (pwdlib)
- **Server:** Uvicorn

## Quick Start

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd dise-api

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env           # then edit .env with your values

# 5. Set up the database and run migrations
alembic upgrade head

# 6. Start the dev server
fastapi dev app/main.py
```

The API is now running at `http://127.0.0.1:8000`.

## Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://diseuser:yourpassword@localhost:5432/dise_api
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Database Setup

If you don't already have a database and user:

```sql
-- run inside `sudo -u postgres psql`
CREATE USER diseuser WITH PASSWORD 'yourpassword';
CREATE DATABASE dise_api OWNER diseuser;
GRANT ALL PRIVILEGES ON DATABASE dise_api TO diseuser;
```

Then apply migrations:

```bash
alembic upgrade head
```

<details>
<summary>Common Alembic commands</summary>

```bash
alembic current                              # current migration version
alembic history                              # migration history
alembic revision --autogenerate -m "message" # create a new migration
alembic upgrade head                         # apply all pending migrations
alembic downgrade -1                         # roll back one step
```
</details>

## Running in Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Reference

Interactive docs are available once the server is running:

- Swagger UI — `http://127.0.0.1:8000/docs`
- ReDoc — `http://127.0.0.1:8000/redoc`
- OpenAPI schema — `http://127.0.0.1:8000/openapi.json`

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create a new user account |
| `POST` | `/auth/login` | Authenticate and receive a JWT |

## Project Structure

```
dise-api/
├── alembic/          # Database migrations
├── app/
│   ├── api/          # Route handlers (e.g. auth.py)
│   ├── core/         # Config & settings
│   ├── db/           # Database session setup
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic request/response schemas
│   ├── services/       # Business logic
│   ├── utils/          # Shared helpers & enums
│   └── main.py         # App entrypoint
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## Roadmap

- Vehicle management (add, update, delete cars)
- Car availability & search filters
- Booking / rental system
- Role-based access control (admin / user)
- Refresh token support
- User profiles & rental history
- Email verification & password reset
- Rate limiting & structured logging
- Unit & integration test suite

## Contributing

Issues and pull requests are welcome. If you're planning a larger change, open an issue first to discuss the approach.

## License

MIT