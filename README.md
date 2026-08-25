# dise-api

A FastAPI backend for a car rental platform. User authentication is fully implemented; vehicle listings, bookings, and rental management are next.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-active--development-yellow)](.)

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running with Docker](#running-with-docker)
- [Running in Production](#running-in-production)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

- ✅ User registration and JWT-based authentication
- ✅ Secure password hashing with Argon2 (via `pwdlib`)
- ✅ PostgreSQL persistence with SQLAlchemy 2.x
- ✅ Schema-driven migrations with Alembic
- ✅ Request/response validation with Pydantic v2
- 🚧 Vehicle listings, bookings, and rental management (in progress)

## Tech Stack

| Layer      | Technology                      |
| ---------- | ------------------------------- |
| Framework  | FastAPI                         |
| Language   | Python 3.12+                    |
| Database   | PostgreSQL (via SQLAlchemy 2.x) |
| Migrations | Alembic                         |
| Validation | Pydantic v2                     |
| Auth       | JWT + Argon2 (pwdlib)           |
| Server     | Uvicorn                         |

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

Create a `.env` file in the project root with the following variables:

| Variable                      | Description                     | Example                                                      |
| ----------------------------- | ------------------------------- | ------------------------------------------------------------ |
| `DATABASE_URL`                | PostgreSQL connection string    | `postgresql://diseuser:yourpassword@localhost:5432/dise_api` |
| `SECRET_KEY`                  | Secret used to sign JWTs        | `3a7f...` (see below)                                        |
| `ALGORITHM`                   | JWT signing algorithm           | `HS256`                                                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (minutes) | `30`                                                         |

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> **Security note:** never commit `.env` to version control, and use a unique `SECRET_KEY` per environment.

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

## Running with Docker

A `docker-compose.yml` is included to run the API alongside a PostgreSQL instance:

```bash
docker compose up --build
```

This:

- Builds the app image
- Starts PostgreSQL
- Runs the API with the configured environment

Update the `.env` values (or the `environment` section in `docker-compose.yml`) to match your local configuration before starting.

To stop and remove containers:

```bash
docker compose down
```

> If you run into permission issues on Linux, ensure the PostgreSQL data directory (if using a named volume) is owned by the correct UID, or use a fresh volume.

## Running in Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

For production deployments, also consider:

- Running behind a reverse proxy (e.g. Nginx) with HTTPS termination
- Setting `ACCESS_TOKEN_EXPIRE_MINUTES` and `SECRET_KEY` via environment/secret manager, not `.env`
- Enabling structured logging and a process manager (systemd, Docker, or similar)
- Restricting CORS origins and rate-limiting sensitive endpoints (e.g. `/auth/login`)

## API Reference

Interactive docs are available once the server is running:

- Swagger UI — `http://127.0.0.1:8000/docs`
- ReDoc — `http://127.0.0.1:8000/redoc`
- OpenAPI schema — `http://127.0.0.1:8000/openapi.json`

### Endpoints

| Method | Endpoint         | Description                    | Auth Required |
| ------ | ---------------- | ------------------------------ | ------------- |
| `POST` | `/auth/register` | Create a new user account      | No            |
| `POST` | `/auth/login`    | Authenticate and receive a JWT | No            |

More endpoints (vehicles, bookings, rentals) will be documented here as they're implemented — see [Roadmap](#roadmap).

## Project Structure

```text
dise-api/
├── alembic/           # Database migrations
├── app/
│   ├── api/           # Route handlers (e.g. auth.py)
│   ├── core/          # Config & settings
│   ├── db/            # Database session setup
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic request/response schemas
│   ├── services/      # Business logic
│   ├── utils/         # Shared helpers & enums
│   └── main.py        # App entrypoint
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## Testing

```bash
pytest
```

To run with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Add a test suite under `tests/` as features are implemented. See [Roadmap](#roadmap) for planned coverage.

## Roadmap

- [ ] Vehicle listing management (CRUD)
- [ ] Booking and rental flows
- [ ] Role-based access control (admin, staff, customer)
- [ ] Refresh token support
- [ ] Expanded user profile support
- [ ] Automated test suite with CI

See open issues for the current priority list.

## Contributing

Issues and pull requests are welcome. For larger changes, please open an issue first to discuss the approach before submitting a PR.

1. Fork the repo and create a feature branch
2. Make your changes, following the existing project structure
3. Ensure `alembic upgrade head` and the app still start cleanly
4. Run `pytest` and confirm all tests pass
5. Open a pull request with a clear description of the change

## License

MIT
