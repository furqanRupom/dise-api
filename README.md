<p align="center">
  <a href="./app/assets/logo.png"><img src="./app/assets/logo.png" alt="dise+ logo" width="120"></a>
</p>

<h1 align="center">dise+ API</h1>

<p align="center">
  <strong>FastAPI backend for a platform-owned car rental fleet service.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.140%2B-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL"></a>
  <a href="https://redis.io/"><img src="https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis&logoColor=white" alt="Redis"></a>
  <a href="https://docs.celeryq.dev/"><img src="https://img.shields.io/badge/Celery-5.4%2B-37814A?style=flat&logo=celery&logoColor=white" alt="Celery"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat" alt="License"></a>
</p>

---

## Features

- **Authentication & RBAC**: Argon2 hashing, HTTP-only cookie JWTs, Google OAuth2, and role-based access (`customer`, `fleet_staff`, `support`, `admin`).
- **Fleet & Branch Management**: Multi-location inventory, vehicle categorization, specs, and Cloudinary image galleries.
- **Double-Booking Guard**: Database-level concurrency protection using PostgreSQL's `btree_gist` exclusion constraints.
- **Driver License Verification**: Customer document submission with admin review workflow and automated email notifications.
- **Pricing & Cancellations**: Discount coupons and tiered cancellation refund calculations.
- **Async Workers**: Celery + Redis for asynchronous background tasks (emails, OTPs).

---

## Tech Stack

- **Framework**: FastAPI (Python 3.12+)
- **Database & ORM**: PostgreSQL 16, SQLAlchemy 2.0, Alembic
- **Cache & Queue**: Redis 7, Celery
- **Storage & Mail**: Cloudinary, FastAPI-Mail / aiosmtplib

---

## Quick Start

### 1. Clone & Setup Environment

```bash
git clone https://github.com/furqanRupom/dise-api.git
cd dise-api

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

### 2. Start Services (PostgreSQL & Redis)

```bash
docker compose up -d

# Enable btree_gist extension (required for booking constraints)
docker compose exec postgres psql -U diseuser -d disedb -c "CREATE EXTENSION IF NOT EXISTS btree_gist;"
```

### 3. Run Migrations & Seed Data

```bash
alembic upgrade head
python scripts/seed_data.py
```

### 4. Run Application

```bash
# Terminal 1: API Server
fastapi dev app/main.py
# API runs at http://127.0.0.1:8000 (Swagger docs: http://127.0.0.1:8000/docs)

# Terminal 2: Celery Worker
celery -A app.core.celery.celery_app worker --loglevel=info
```

---

## Test Accounts

When populated via `seed_data.py`, use password **`Password123!`**:

| Role | Email |
| :--- | :--- |
| **Admin** | `admin@example.com` |
| **Support** | `support@example.com` |
| **Fleet Staff** | `fleet@example.com` |
| **Customer (Approved License)** | `customer1@example.com` |
| **Customer (Pending License)** | `customer2@example.com` |

---

## API Documentation

Interactive API documentation is automatically generated and accessible when the server is running:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## License

This project is licensed under the [MIT License](LICENSE).
