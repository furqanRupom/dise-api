<p align="center">
  <a href="./app/assets/logo.png"><img src="./app/assets/logo.png" alt="dise+ logo" width="110"></a>
</p>

<h1 align="center">dise+ api</h1>

<p align="center">
  <strong>fastapi backend for a platform-owned car rental fleet service.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12%2b-3776ab?style=flat&logo=python&logocolor=white" alt="python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/fastapi-0.140%2b-009688?style=flat&logo=fastapi&logocolor=white" alt="fastapi"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/postgresql-16-4169e1?style=flat&logo=postgresql&logocolor=white" alt="postgresql"></a>
  <a href="https://redis.io/"><img src="https://img.shields.io/badge/redis-7-dc382d?style=flat&logo=redis&logocolor=white" alt="redis"></a>
  <a href="https://docs.celeryq.dev/"><img src="https://img.shields.io/badge/celery-5.4%2b-37814a?style=flat&logo=celery&logocolor=white" alt="celery"></a>
  <a href="license"><img src="https://img.shields.io/badge/license-mit-blue.svg?style=flat" alt="license"></a>
</p>

---

## overview

**dise+** is a restful backend api designed for a platform-owned car rental fleet service. unlike peer-to-peer marketplaces, the platform directly owns and manages its vehicle inventory across physical branch locations.

it handles the entire rental lifecycle: driver's license verification, multi-branch vehicle availability, concurrency-safe reservations, stripe payment and deposit holds, and automated celery background operations.

---

## features

- **auth & rbac**: argon2 hashing, http-only cookie jwts, google oauth2, and role permissions (`customer`, `fleet_staff`, `support`, `admin`).
- **fleet & locations**: multi-branch vehicle catalog, specs, real-time availability, and cloudinary media storage.
- **double-booking guard**: postgresql `btree_gist` exclusion constraints to prevent overlapping reservations at the db level.
- **driver verification**: driving license upload, document ocr/verification pipeline, and admin approval workflows.
- **payments & coupons**: stripe checkout, deposit holds, automated cancellation refund policies, and promo codes.
- **background tasks**: celery + redis for scheduled task execution (reservation expiration, payment checks) and emails.

---

## tech stack

| category          | technologies                                           |
| :---------------- | :----------------------------------------------------- |
| **core**          | python 3.12+, fastapi, pydantic v2                     |
| **database**      | postgresql 16, sqlalchemy 2.0, alembic                 |
| **queue & cache** | redis 7, celery + celery beat                          |
| **integrations**  | stripe (payments), cloudinary (media), mailtrap / smtp |

---

## getting started

### 1. environment setup

```bash
# clone and enter repo
git clone https://github.com/furqanrupom/dise-api.git
cd dise-api

# virtual environment & dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# copy environment file and configure secrets
cp .env.example .env
```

### 2. start services

```bash
# start postgresql & redis
docker compose up -d

# enable btree_gist extension (required for booking constraints)
docker compose exec postgres psql -u diseuser -d disedb -c "create extension if not exists btree_gist;"
```

### 3. migrations & seed data

```bash
alembic upgrade head
python scripts/seed_data.py
```

### 4. run the application

```bash
# terminal 1: api server (http://127.0.0.1:8000)
fastapi dev app/main.py

# terminal 2: celery worker & beat
celery -a app.core.celery.celery_app worker --beat --loglevel=info
```

---

## seed accounts

seeded via `scripts/seed_data.py` (default password: **`password123!`**):

| role                    | email                   |
| :---------------------- | :---------------------- |
| **admin**               | `admin@example.com`     |
| **support**             | `support@example.com`   |
| **fleet staff**         | `fleet@example.com`     |
| **customer (verified)** | `customer1@example.com` |
| **customer (pending)**  | `customer2@example.com` |

---

## api documentation

when the api server is running, interactive docs are available at:

- **swagger ui**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **redoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## license

distributed under the [mit license](license).
