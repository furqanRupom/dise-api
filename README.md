<p align="center">
  <a href="./app/assets/logo.png"><img src="./app/assets/logo.png" alt="dise+ logo" width="140"></a>
</p>

<h1 align="center">dise+</h1>
<p align="center">A FastAPI backend for a platform-owned car rental service.</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12%2B-blue" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/framework-FastAPI-009688" alt="FastAPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
  <a href="."><img src="https://img.shields.io/badge/status-active--development-yellow" alt="Status"></a>
</p>

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running Background Tasks (Celery)](#running-background-tasks-celery)
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
- ✅ OAuth login support
- ✅ Asynchronous email delivery (OTP, forgot-password, license decisions) via Celery
- ✅ Redis-backed OTP, queue broker, and session/cache layer
- ✅ Cloudinary integration for image uploads (avatars, vehicle images)
- ✅ Location management (pickup/drop-off branches)
- ✅ Vehicle category management
- ✅ Coupon management
- ✅ PostgreSQL persistence with SQLAlchemy 2.x
- ✅ Schema-driven migrations with Alembic
- ✅ Request/response validation with Pydantic v2
- 🚧 Vehicle listings & availability (in progress)
- 🚧 Booking, payment, and rental lifecycle (in progress)
- 🚧 Condition reports & maintenance blocks (models defined, endpoints pending)
- 🚧 Notifications & audit logs (models defined, endpoints pending)

## Tech Stack

| Layer          | Technology                      |
| -------------- | ------------------------------- |
| Framework      | FastAPI                         |
| Language       | Python 3.12+                    |
| Database       | PostgreSQL (via SQLAlchemy 2.x) |
| Migrations     | Alembic                         |
| Validation     | Pydantic v2                     |
| Auth           | JWT + Argon2 (pwdlib) + OAuth   |
| Cache / Broker | Redis                           |
| Task Queue     | Celery                          |
| Media Storage  | Cloudinary                      |
| Email          | SMTP client + HTML templates    |
| Server         | Uvicorn                         |

## Quick Start

```bash
# 1. Clone and enter the project
git clone https://github.com/furqanRupom/dise-api.git
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

# 7. Start the Celery worker (in a separate terminal)
celery -A app.core.celery.celery_app worker --loglevel=info
```

The API is now running at `http://127.0.0.1:8000`.

## Configuration

Create a `.env` file in the project root with the following variables:

| Variable                      | Description                     | Example                                                    |
| ----------------------------- | ------------------------------- | ---------------------------------------------------------- |
| `DATABASE_URL`                | PostgreSQL connection string    | `postgresql://diseuser:yourpassword@localhost:5432/disedb` |
| `SECRET_KEY`                  | Secret used to sign JWTs        | `3a7f...` (see below)                                      |
| `ALGORITHM`                   | JWT signing algorithm           | `HS256`                                                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (minutes) | `30`                                                       |
| `REDIS_URL`                   | Redis connection string         | `redis://localhost:6379/0`                                 |
| `CLOUDINARY_URL`              | Cloudinary connection string    | `cloudinary://<key>:<secret>@<cloud_name>`                 |
| `MAIL_USERNAME`               | SMTP username                   | `noreply@dise.app`                                         |
| `MAIL_PASSWORD`               | SMTP password / app password    | `********`                                                 |
| `MAIL_FROM`                   | From address for outgoing email | `noreply@dise.app`                                         |
| `MAIL_SERVER`                 | SMTP server host                | `smtp.gmail.com`                                           |

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
CREATE DATABASE disedb OWNER diseuser;
GRANT ALL PRIVILEGES ON DATABASE disedb TO diseuser;

```

`btree_gist` is required for the exclusion constraints used to prevent double-booking:

```bash
psql -U diseuser -d disedb -f scripts/sql/btree_gist_setup.sql

```

Then apply migrations:

```bash
alembic upgrade head

```

```bash
alembic current                              # current migration version
alembic history                              # migration history
alembic revision --autogenerate -m "message" # create a new migration
alembic upgrade head                         # apply all pending migrations
alembic downgrade -1                         # roll back one step

```

To load sample data for local development:

```bash
python scripts/seed_data.py

```

## Running Background Tasks (Celery)

Background tasks (such as sending transactional emails and processing notifications) are managed by Celery using Redis as the message broker.

### Start the Worker Node

Run this command in a terminal where your virtual environment is active:

```bash
celery -A app.core.celery.celery_app worker --loglevel=info

```

To run with a custom worker name (helpful when running multiple worker instances):

```bash
celery -A app.core.celery.celery_app worker --loglevel=info -n email_worker@%h

```

## Running with Docker

A `docker-compose.yml` is included to run the API, PostgreSQL, Redis, and the Celery worker:

```bash
docker compose up --build

```

This:

- Builds the application container
- Starts PostgreSQL and Redis
- Runs the FastAPI web application
- Starts the Celery worker process for background tasks

To stop and remove containers:

```bash
docker compose down

```

## Running in Production

Start the FastAPI app server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

```

Start the Celery worker process (using `systemd`, `supervisord`, or container orchestration):

```bash
celery -A app.core.celery.celery_app worker --loglevel=warning --concurrency=4

```

For production deployments, also consider:

- Running behind a reverse proxy (e.g. Nginx) with HTTPS termination
- Setting `SECRET_KEY`, `CLOUDINARY_URL`, and mail credentials via a secret manager, not `.env`
- Enabling structured logging and a process manager (systemd, Docker, or similar)
- Restricting CORS origins and rate-limiting sensitive endpoints (e.g. `/auth/login`)

## API Reference

Interactive docs are available once the server is running:

- Swagger UI — `http://127.0.0.1:8000/docs`
- ReDoc — `http://127.0.0.1:8000/redoc`
- OpenAPI schema — `http://127.0.0.1:8000/openapi.json`

### Endpoints

| Method | Endpoint              | Description                    | Auth Required |
| ------ | --------------------- | ------------------------------ | ------------- |
| `POST` | `/auth/register`      | Create a new user account      | No            |
| `POST` | `/auth/login`         | Authenticate and receive a JWT | No            |
| `GET`  | `/users/me`           | Get current user profile       | Yes           |
| `GET`  | `/locations`          | List pickup/drop-off locations | No            |
| `POST` | `/locations`          | Create a location              | Admin         |
| `GET`  | `/vehicle-categories` | List vehicle categories        | No            |
| `POST` | `/vehicle-categories` | Create a vehicle category      | Admin         |
| `GET`  | `/coupons`            | List coupons                   | Admin         |
| `POST` | `/coupons`            | Create a coupon                | Admin         |

## Project Structure

```text
dise-api/
├── alembic/           # Database migrations
├── app/
│   ├── api/           # Route handlers (auth, user, location, coupon, vehicle_category)
│   ├── assets/        # Static assets (logo, etc.)
│   ├── core/          # Config, security, OAuth, mail, Cloudinary, Celery, RBAC
│   ├── db/            # Database + Redis session setup
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic request/response schemas
│   ├── services/      # Business logic
│   ├── templates/     # Email templates (OTP, forgot password)
│   ├── utils/         # Shared helpers & enums
│   └── main.py        # App entrypoint
├── scripts/
│   ├── seed_data.py   # Local dev seed data
│   └── sql/           # Raw SQL setup (btree_gist, etc.)
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

## Roadmap

- [x] User registration and authentication
- [x] Location management
- [x] Vehicle category management
- [x] Coupon management
- [x] Celery background task processing
- [ ] Vehicle listing management (CRUD) + availability engine
- [ ] Booking creation, state machine, and cancellation
- [ ] Payment capture, deposit holds, and refunds (Stripe)
- [ ] Check-in/check-out and condition reports
- [ ] Role-based access control (admin, staff, support, customer)
- [ ] Refresh token support
- [ ] Automated test suite with CI

## Contributing

Issues and pull requests are welcome. For larger changes, please open an issue first to discuss the approach before submitting a PR.

1. Fork the repo and create a feature branch
2. Make your changes, following the existing project structure
3. Ensure `alembic upgrade head` and the app still start cleanly
4. Run `pytest` and confirm all tests pass
5. Open a pull request with a clear description of the change

## License

MIT
