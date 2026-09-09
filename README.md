<p align="center">
  <a href="./app/assets/logo.png"><img src="./app/assets/logo.png" alt="dise+ logo" width="140"></a>
</p>

<h1 align="center">dise+ API</h1>
<p align="center">
  <strong>Production-ready FastAPI backend for a platform-owned car rental service.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.140%2B-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
  <a href="https://redis.io/"><img src="https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis&logoColor=white" alt="Redis"></a>
  <a href="https://docs.celeryq.dev/"><img src="https://img.shields.io/badge/Celery-5.4%2B-37814A?style=flat&logo=celery&logoColor=white" alt="Celery"></a>
  <a href="https://www.sqlalchemy.org/"><img src="https://img.shields.io/badge/SQLAlchemy-2.0%2B-D71F00?style=flat&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat" alt="License"></a>
</p>

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Quick Start Guide](#quick-start-guide)
- [Pre-seeded Test Accounts](#pre-seeded-test-accounts)
- [Configuration (.env)](#configuration-env)
- [Database Setup & Migrations](#database-setup--migrations)
- [Background Tasks (Celery & Redis)](#background-tasks-celery--redis)
- [Infrastructure with Docker](#infrastructure-with-docker)
- [API Reference & Endpoints](#api-reference--endpoints)
- [Project Directory Structure](#project-directory-structure)
- [Production Deployment](#production-deployment)
- [Testing & Quality](#testing--quality)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**dise+** is a backend system engineered for **platform-owned car rental fleets** (unlike peer-to-peer marketplaces). It powers the complete rental lifecycle: vehicle category classification, multi-branch fleet inventory, user identity and driver license verification, dynamic pricing & coupons, concurrency-safe double-booking prevention, condition check-in/check-out inspections, tiered cancellation refunds, and asynchronous email notifications.

---

## System Architecture

```mermaid
flowchart TD
    Client["Web / Mobile Client"] -->|HTTP / Cookie JWT| FastAPI["FastAPI Application (Port 8000)"]
    
    subgraph Core App
        FastAPI --> Auth["Auth & RBAC<br/>(Argon2 + OAuth2)"]
        FastAPI --> Routers["API Routers<br/>(/v1/auth, /vehicles, etc.)"]
        FastAPI --> ORM["SQLAlchemy 2.x ORM"]
    end

    subgraph Data & Cache
        FastAPI -->|OTP, Sessions, Cache| Redis[("Redis 7<br/>Broker & Cache")]
        ORM -->|btree_gist Constraints| Postgres[("PostgreSQL 16<br/>disedb")]
    end

    subgraph Asynchronous Workers
        Redis -->|Queue: tasks| Celery["Celery Worker Node"]
        Celery -->|Transactional Emails| SMTP["SMTP / Mailtrap"]
    end

    subgraph Cloud Storage
        FastAPI -->|Direct SDK Uploads| Cloudinary["Cloudinary CDN<br/>(Avatars, Vehicles, Licenses)"]
    end
```

---

## Key Features

- **Robust Authentication & Security**
  - Argon2 password hashing via `pwdlib`.
  - Secure HTTP-only cookie-based JWT flow (`access_token` and `refresh_token`).
  - Google OAuth2 social login integration.
  - Granular Role-Based Access Control (RBAC): `customer`, `fleet_staff`, `support`, and `admin`.
- **Driver License Verification Workflow**
  - Customers submit driver license credentials along with front/back document photos.
  - Admin/Fleet review queue with instant approval/rejection.
  - Asynchronous email notifications dispatched upon review decisions.
- **Fleet & Catalog Management**
  - Multi-branch location support (pickup and return hubs).
  - Vehicle categorization (Economy, Sedan, SUV, Luxury, Minivan, Pickup).
  - Comprehensive vehicle metadata: transmission, fuel type, seating, mileage, daily rates, and status (`available`, `booked`, `in_maintenance`, `retired`).
  - Cloudinary-backed multi-image galleries per vehicle.
- **Database-Level Concurrency & Double-Booking Protection**
  - Utilizes PostgreSQL's `btree_gist` extension and SQLAlchemy `ExcludeConstraint`.
  - Guarantees at the database engine level that no vehicle can have overlapping confirmed or active booking date ranges.
- **Promotions & Refund Engine**
  - Flexible discount coupons supporting both percentage and fixed-amount deductions with usage tracking.
  - Tiered cancellation refund engine computing refund quotes based on notice hours prior to rental start.
- **Asynchronous Task Queue**
  - Celery worker backed by Redis for offloading email dispatch (OTP codes, password reset links, license decision updates).
- **Developer-Friendly Ergonomics**
  - Interactive OpenAPI Swagger UI (`/docs`) and ReDoc (`/redoc`).
  - Automated database seed script with realistic mock data and preset credentials.
  - Strict data validation with Pydantic v2.

---

## Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) (0.140+) | High-performance asynchronous REST API framework |
| **Runtime** | Python 3.12+ | Modern Python runtime |
| **Database** | PostgreSQL 16 | Primary relational database with ACID guarantees |
| **ORM & Migrations** | SQLAlchemy 2.x + Alembic | Declarative mapping, session management, schema migrations |
| **Validation** | Pydantic v2 / Pydantic-Settings | Request/response schemas and environment configuration |
| **Task Queue & Broker** | Celery + Redis 7 | Distributed asynchronous task execution and message broker |
| **Authentication** | Argon2 (`pwdlib`) + PyJWT + Authlib | Password hashing, JWT token rotation, and Google OAuth2 |
| **Media Storage** | Cloudinary SDK | Cloud image upload, optimization, and asset CDN |
| **Email Delivery** | `fastapi-mail` / `aiosmtplib` | Transactional email delivery with Jinja2 HTML templates |
| **Containerization** | Docker Compose | Local backing infrastructure (Postgres & Redis) |

---

## Quick Start Guide

### Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [Docker & Docker Compose](https://docs.docker.com/get-docker/) (for local Postgres & Redis)
- [Git](https://git-scm.com/)

---

### Step 1: Clone and Enter the Project

```bash
git clone https://github.com/furqanRupom/dise-api.git
cd dise-api
```

### Step 2: Set Up Virtual Environment

```bash
python3 -m venv .venv

# Linux / macOS:
source .venv/bin/activate

# Windows (Command Prompt):
# .venv\Scripts\activate.bat

# Windows (PowerShell):
# .venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy the example environment configuration:

```bash
cp .env.example .env
```

Open `.env` and verify or customize your secrets (see [Configuration (.env)](#configuration-env) below).

### Step 5: Start Supporting Services (PostgreSQL & Redis)

Use Docker Compose to launch PostgreSQL 16 and Redis 7 in the background:

```bash
docker compose up -d
```

Verify the containers are running:

```bash
docker compose ps
```

### Step 6: Initialize Database & Run Migrations

1. Ensure the PostgreSQL `btree_gist` extension is active:
   ```bash
   docker compose exec postgres psql -U diseuser -d disedb -c "CREATE EXTENSION IF NOT EXISTS btree_gist;"
   ```
2. Apply all Alembic schema migrations:
   ```bash
   alembic upgrade head
   ```

### Step 7: (Optional) Seed Sample Data

Populate your database with realistic branch locations, vehicle categories, vehicles, discount coupons, refund tiers, and pre-configured accounts:

```bash
python scripts/seed_data.py
```

### Step 8: Run the Application & Background Worker

**Terminal 1 — FastAPI Server:**
```bash
fastapi dev app/main.py
# or: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Celery Task Worker:**
```bash
celery -A app.core.celery.celery_app worker --loglevel=info
```

Your API is now live at **`http://127.0.0.1:8000`**!

---

## Pre-seeded Test Accounts

When running `python scripts/seed_data.py`, the following demo accounts are created:

| Role | Email | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `Password123!` | Full administrative access across all endpoints |
| **Support** | `support@example.com` | `Password123!` | Support agent with customer oversight |
| **Fleet Staff** | `fleet@example.com` | `Password123!` | Fleet management and vehicle logistics |
| **Customer** | `customer1@example.com` | `Password123!` | Customer account with approved driver license |
| **Customer** | `customer2@example.com` | `Password123!` | Customer account with pending driver license |

---

## Configuration (.env)

The application uses `pydantic-settings` to parse and validate settings from `.env`. Below is a breakdown of all variables:

| Group | Variable | Description | Default / Example |
| :--- | :--- | :--- | :--- |
| **App** | `APP_NAME` | Name of the application | `Dise API` |
| | `VERSION` | API version string | `1.0.0` |
| | `FRONTEND_HOST` | Allowed frontend origin for CORS | `http://localhost:3000` |
| **Auth & JWT** | `ALGORITHMS` | Algorithm used for JWT encoding | `HS256` |
| | `SECRET_ACCESS_TOKEN` | Secret key for signing access tokens | *64-char hex string* |
| | `SECRET_REFRESH_TOKEN` | Secret key for signing refresh tokens | *64-char hex string* |
| | `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan | `15` |
| | `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifespan | `7` |
| **Database** | `DATABASE_URL` | PostgreSQL connection URI | `postgresql://diseuser:disepassword@localhost:5432/disedb` |
| **Redis** | `REDIS_HOST` | Redis hostname | `localhost` |
| | `REDIS_PORT` | Redis port | `6379` |
| | `REDIS_DB` | Redis database index | `0` |
| | `REDIS_URL` | Optional complete Redis connection string | `redis://localhost:6379/0` |
| **Email (SMTP)** | `MAIL_USERNAME` | SMTP account username | Mailtrap or SMTP username |
| | `MAIL_PASSWORD` | SMTP account password | Mailtrap or SMTP password |
| | `MAIL_FROM` | Outgoing sender email address | `noreply@dise.app` |
| | `MAIL_FROM_NAME` | Outgoing sender display name | `Dise App` |
| | `MAIL_SERVER` | SMTP host server | `sandbox.smtp.mailtrap.io` |
| | `MAIL_PORT` | SMTP port | `587` |
| **OAuth** | `GOOGLE_CLIENT_ID` | Google OAuth2 Client ID | *Your Client ID* |
| | `GOOGLE_CLIENT_SECRET` | Google OAuth2 Client Secret | *Your Client Secret* |
| **Storage** | `STORAGE_BACKEND` | Storage adapter name | `cloudinary` |
| | `CLOUDINARY_CLOUD_NAME` | Cloudinary account cloud name | *Your Cloud Name* |
| | `CLOUDINARY_API_KEY` | Cloudinary API key | *Your API Key* |
| | `CLOUDINARY_API_SECRET` | Cloudinary API secret | *Your API Secret* |
| | `CLOUDINARY_FOLDER` | Target upload folder in Cloudinary | `uploads` |

### Generate Cryptographic Secrets

Generate strong random secrets for `SECRET_ACCESS_TOKEN` and `SECRET_REFRESH_TOKEN`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> [!WARNING]
> Never commit your `.env` file to source control. In production environments, inject these values using a secure secrets manager or orchestration environment variables.

---

## Database Setup & Migrations

### Double-Booking Guard (`btree_gist`)

The `bookings` table uses an `ExcludeConstraint` to prevent overlapping date reservations for the same vehicle at the database layer. This requires the PostgreSQL `btree_gist` extension:

```bash
# Apply via SQL script
psql -U diseuser -d disedb -f scripts/sql/btree_gist_setup.sql

# Or execute directly via Docker
docker compose exec postgres psql -U diseuser -d disedb -c "CREATE EXTENSION IF NOT EXISTS btree_gist;"
```

### Alembic Migration Workflow

| Action | Command |
| :--- | :--- |
| **Check Current Version** | `alembic current` |
| **View Revision History** | `alembic history --verbose` |
| **Generate New Migration** | `alembic revision --autogenerate -m "describe changes"` |
| **Apply All Pending Migrations** | `alembic upgrade head` |
| **Roll Back One Migration** | `alembic downgrade -1` |

---

## Background Tasks (Celery & Redis)

Background operations (such as sending one-time passcodes, password reset instructions, and driver license approval emails) are offloaded to Celery to keep HTTP requests fast.

### Starting Workers

```bash
# Standard worker
celery -A app.core.celery.celery_app worker --loglevel=info

# Named worker (useful when running multiple worker instances)
celery -A app.core.celery.celery_app worker --loglevel=info -n email_worker@%h
```

Tasks are autodiscovered from `app/tasks/` (e.g., `send_notification_task` in `app/tasks/notifications.py`).

---

## Infrastructure with Docker

The provided `docker-compose.yml` spins up the essential backing datastores:

- **PostgreSQL 16**: Port `5432:5432`, persists data to `postgres_data` volume.
- **Redis 7**: Port `6379:6379`, persists data to `redis_data` volume.

```bash
# Start backing services in background
docker compose up -d

# View live container logs
docker compose logs -f

# Stop and remove containers (preserving data volumes)
docker compose down

# Stop and wipe data volumes
docker compose down -v
```

---

## API Reference & Endpoints

Once the application is running, visit:
- **Swagger UI**: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON**: [`http://127.0.0.1:8000/openapi.json`](http://127.0.0.1:8000/openapi.json)

### Authentication (`/v1/auth`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/v1/auth/register` | Register new user account | Public |
| `POST` | `/v1/auth/login` | Authenticate with email/password; sets HTTP-only cookies | Public |
| `POST` | `/v1/auth/send-otp` | Send email verification OTP code | Public |
| `POST` | `/v1/auth/verify-email` | Verify email address using received OTP | Public |
| `POST` | `/v1/auth/refresh-token` | Rotate access and refresh tokens | Refresh Cookie |
| `POST` | `/v1/auth/forgot-password` | Request password reset code via email | Public |
| `POST` | `/v1/auth/reset-password` | Reset password using verified code | Public |
| `POST` | `/v1/auth/logout` | Invalidate session and clear auth cookies | Authenticated |
| `GET` | `/v1/auth/get-me` | Get current authenticated user profile | Authenticated |
| `GET` | `/v1/auth/google/login` | Initiate Google OAuth2 login flow | Public |
| `GET` | `/v1/auth/google/callback` | OAuth2 callback redirect endpoint | Public |

### User & Driver Licensing (`/v1/user`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `PATCH` | `/v1/user/profile` | Update personal details (name, phone, address, DOB) | Authenticated |
| `PATCH` | `/v1/user/avatar` | Upload and update profile avatar | Authenticated |
| `DELETE` | `/v1/user/delete-account` | Soft-delete user account | Authenticated |
| `POST` | `/v1/user/me/license` | Submit driver's license details and images | Customer |
| `GET` | `/v1/user/admin/licenses` | View queue of pending/reviewed driver licenses | Admin / Staff |
| `PUT` | `/v1/user/admin/license/{user_id}` | Approve or reject driver license (triggers email) | Admin |

### Branch Locations (`/v1/location`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/v1/location/` | List all pickup / drop-off branch locations | Public |
| `GET` | `/v1/location/{location_id}` | Get details of a branch location | Public |
| `POST` | `/v1/location/` | Create a new branch location | Admin |
| `PUT` | `/v1/location/{location_id}` | Update branch location details | Admin |
| `DELETE` | `/v1/location/{location_id}` | Remove a branch location | Admin |

### Vehicle Categories (`/vehicle-categories`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/vehicle-categories/` | List all active vehicle categories | Public |
| `GET` | `/vehicle-categories/{id}` | Get category specifications and description | Public |
| `POST` | `/vehicle-categories/` | Create a vehicle category | Admin |
| `PUT` | `/vehicle-categories/{id}` | Update vehicle category | Admin |
| `PATCH` | `/vehicle-categories/{id}` | Toggle category active/inactive status | Admin |
| `DELETE` | `/vehicle-categories/{id}` | Delete a vehicle category | Admin |

### Vehicles Fleet (`/vehicles`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/vehicles/` | Search & filter vehicles (by category, location, fuel, transmission, price) | Public |
| `GET` | `/vehicles/{vehicle_id}` | Get full vehicle details, branch location, and photos | Public |
| `POST` | `/vehicles/` | Register a new vehicle into the fleet | Admin |
| `PUT` | `/vehicles/{vehicle_id}` | Update vehicle specifications or status | Admin |
| `DELETE` | `/vehicles/{vehicle_id}` | Soft-delete / decommission a vehicle | Admin |
| `POST` | `/vehicles/{vehicle_id}/images` | Upload vehicle gallery images to Cloudinary | Admin |

### Coupons & Discounts (`/v1/coupon`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/v1/coupon/` | List all discount coupons | Admin / Staff |
| `GET` | `/v1/coupon/{coupon_id}` | Get coupon by ID | Admin / Staff |
| `POST` | `/v1/coupon/` | Create a new discount coupon | Admin |
| `PUT` | `/v1/coupon/{coupon_id}` | Update coupon properties and limits | Admin |
| `DELETE` | `/v1/coupon/{coupon_id}` | Delete coupon | Admin |
| `PATCH` | `/v1/coupon/{coupon_id}/activate` | Activate a coupon | Admin |
| `PATCH` | `/v1/coupon/{coupon_id}/deactivate` | Deactivate a coupon | Admin |

### Cancellation & Refund Policy (`/refund-policy`)

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/refund-policy/` | List cancellation refund policy tiers | Public |
| `POST` | `/refund-policy/` | Create a new cancellation refund tier | Admin |
| `PUT` | `/refund-policy/{tier_id}` | Update refund policy tier | Admin |
| `DELETE` | `/refund-policy/{tier_id}` | Delete refund policy tier | Admin |
| `POST` | `/refund-policy/quote` | Compute estimated refund amount quote for cancellation | Authenticated |

### System & Health

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API status, health check, version, and documentation links | Public |

---

## Project Directory Structure

```text
dise-api/
├── alembic/                  # Database migration scripts & env
├── app/
│   ├── api/                  # FastAPI APIRouter endpoint handlers
│   │   ├── auth.py           # Authentication, OTP, OAuth, token rotation
│   │   ├── coupon.py         # Discount & coupon management
│   │   ├── location.py       # Rental branch hubs & locations
│   │   ├── refund_policy.py  # Cancellation tiers & refund quoting
│   │   ├── user.py           # Profiles, avatars, driver license review
│   │   ├── vehicle.py        # Fleet CRUD, filtering, image uploads
│   │   └── vehicle_category.py # Category classification
│   ├── assets/               # Branding assets (logos, images)
│   ├── core/                 # Core utilities & security layer
│   │   ├── celery.py         # Celery instance configuration
│   │   ├── cloudinary.py     # Cloudinary CDN client
│   │   ├── config.py         # Pydantic Settings & environment parsing
│   │   ├── dependencies.py   # Auth, RBAC, DB & Redis FastAPI dependencies
│   │   ├── mail.py           # Mail configurations & email helpers
│   │   ├── mail_client.py    # Async email client implementation
│   │   ├── oauth.py          # Google OAuth2 integration
│   │   └── security.py       # Password hashing (Argon2), JWT signing
│   ├── db/                   # Database & cache engine setup
│   │   ├── database.py       # SQLAlchemy engine & session factory
│   │   └── redis.py          # Redis connection pool & helpers
│   ├── models/               # SQLAlchemy 2.x declarative ORM models
│   │   ├── audit_logs.py     # Administrative audit trail records
│   │   ├── base.py           # TimestampMixin & SoftDeleteMixin
│   │   ├── booking.py        # Booking models & ExclusionConstraints
│   │   ├── condition_reports.py # Check-in / check-out vehicle damage logs
│   │   ├── coupons.py        # Coupons and usage tracking
│   │   ├── enums.py          # Domain enums (Roles, Statuses, Types)
│   │   ├── location.py       # Branch locations
│   │   ├── maintenance.py    # Vehicle maintenance downtime blocks
│   │   ├── notifications.py  # User notification logs
│   │   ├── payments.py       # Payments, holds, refunds
│   │   ├── refund_policy.py  # Tiered cancellation refund policies
│   │   ├── reviews.py        # Customer ratings & reviews
│   │   ├── user.py           # User accounts & licensing metadata
│   │   └── vehicle.py        # Vehicles, categories, image galleries
│   ├── schemas/              # Pydantic request & response models
│   ├── services/             # Business logic layer
│   ├── tasks/                # Celery asynchronous task definitions
│   │   └── notifications.py  # Background email dispatch tasks
│   ├── templates/            # Jinja2 HTML email templates (OTP, reset, etc.)
│   ├── utils/                # Enums, serializers, and general utilities
│   └── main.py               # FastAPI application factory & middleware setup
├── scripts/
│   ├── seed_data.py          # Development data seeder (Faker)
│   └── sql/
│       └── btree_gist_setup.sql # btree_gist extension setup script
├── .env.example              # Example environment configuration
├── alembic.ini               # Alembic configuration
├── docker-compose.yml        # Docker Compose configuration (Postgres & Redis)
├── requirements.txt          # Python dependency manifest
└── README.md                 # Project documentation
```

---

## Production Deployment

When deploying to a production Linux/cloud server:

### 1. Run the FastAPI Application Server

Use `uvicorn` with multiple worker processes behind a reverse proxy (Nginx, Caddy, or Cloudflare):

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --proxy-headers \
  --forwarded-allow-ips='*'
```

### 2. Run the Celery Worker Process

Manage the Celery worker process with `systemd`, `supervisord`, or Docker:

```bash
celery -A app.core.celery.celery_app worker \
  --loglevel=warning \
  --concurrency=4 \
  --max-tasks-per-child=1000
```

### 3. Production Best Practices

- **Reverse Proxy & SSL**: Terminate TLS at Nginx or Cloudflare, and configure HTTP strict transport security (HSTS).
- **CORS Configuration**: Restrict `FRONTEND_HOST` to your production frontend domain (e.g. `https://dise.app`).
- **Secrets**: Inject secrets (`SECRET_ACCESS_TOKEN`, `SECRET_REFRESH_TOKEN`, `DATABASE_URL`, `CLOUDINARY_*`) via your host's environment or a secret manager (AWS Secrets Manager, HashiCorp Vault).
- **Rate Limiting**: Add rate-limiting on sensitive authentication endpoints (`/v1/auth/login`, `/v1/auth/send-otp`) to mitigate brute-force attacks.
- **Monitoring & Error Tracking**: Initialize Sentry (installed via `sentry-sdk`) in `app/main.py`.

---

## Testing & Quality

To install development and testing tools:

```bash
pip install pytest pytest-asyncio httpx ruff
```

### Running Tests

```bash
# Run test suite
pytest

# Run tests with test coverage report
pytest --cov=app --cov-report=term-missing
```

### Code Formatting & Linting

```bash
# Check code style with ruff
ruff check .

# Automatically apply formatting
ruff format .
```

---

## Contributing

Contributions, issues, and feature suggestions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Verify tests pass and migrations work: `alembic upgrade head`
5. Push to your branch: `git push origin feat/your-feature-name`
6. Open a Pull Request with a descriptive summary

---

## License

This project is licensed under the [MIT License](LICENSE).
