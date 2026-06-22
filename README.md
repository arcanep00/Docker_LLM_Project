# Transaction Intelligence API

A FastAPI + PostgreSQL + Redis + Celery backend that ingests transaction CSV
files, cleans and normalizes the data, detects anomalies, categorizes merchants
using Google Gemini, generates a financial summary, and persists everything for
querying via a REST API.

This repository is the solution to a **Backend + DevOps assignment**.

---

## Project Overview

A client uploads a CSV of financial transactions. The upload returns
immediately with a `job_id` while the heavy work runs asynchronously in a
Celery worker:

1. The CSV is cleaned (dates, amounts, statuses, missing categories, duplicates).
2. Anomalies are detected (amount outliers and currency mismatches).
3. Merchants with missing categories are classified by Google Gemini.
4. A financial summary (totals, top merchants, anomaly count, risk level and an
   AI narrative) is generated.
5. Transactions and the summary are persisted to PostgreSQL.
6. The job status is tracked throughout (`pending → PROCESSING → COMPLETED/FAILED`).

Clients then poll the API for job status and fetch the processed transactions
and summary.

---

## Architecture

```
                 ┌─────────────┐      enqueue job        ┌──────────────┐
   CSV upload →  │   FastAPI    │ ───────────────────────▶│    Redis     │
                 │  (web/API)   │       (broker)          │  (broker +   │
                 │              │ ◀───────────────────────│   backend)   │
                 └──────┬───────┘                         └──────┬───────┘
                        │ read/write                              │ consume
                        ▼                                         ▼
                 ┌─────────────┐                          ┌──────────────┐
                 │ PostgreSQL  │ ◀────────────────────────│ Celery worker│
                 │  (jobs,     │   persist results        │  pipeline    │
                 │ transactions│                          │              │
                 │  summaries) │                          └──────┬───────┘
                 └─────────────┘                                 │ classify / summarize
                                                                 ▼
                                                          ┌──────────────┐
                                                          │ Google Gemini│
                                                          └──────────────┘
```

### Project structure

```
app/
├── main.py                  # FastAPI app + router wiring + health check
├── config.py                # Environment configuration
├── api/
│   └── job_routers.py       # All /jobs endpoints
├── db/
│   ├── base.py              # SQLAlchemy declarative base
│   ├── database.py          # Engine + SessionLocal
│   └── dependency.py        # get_db FastAPI dependency
├── models/                  # SQLAlchemy ORM models
│   ├── job.py
│   ├── Transaction.py
│   └── job_summary.py
├── schemas/                 # Pydantic request/response models
├── services/                # Business logic
│   ├── csv_service.py       # Cleaning pipeline
│   ├── anomaly_service.py   # Anomaly detection rules
│   ├── llm_service.py       # Gemini merchant categorization
│   ├── summary_service.py   # Summary + narrative generation
│   ├── transaction_service.py
│   └── job_service.py
├── workers/
│   ├── celery_app.py        # Celery application
│   └── tasks.py             # process_csv_job orchestration
└── create_tables.py         # Convenience create_all (Alembic is the source of truth)
migrations/                  # Alembic migration environment
tests/                       # Pytest suite
```

---

## Features

- **Async CSV ingestion** via FastAPI + Celery (non-blocking uploads).
- **Data cleaning**: ISO date normalization, numeric amount parsing, status
  upper-casing, missing-category fill, duplicate removal.
- **Anomaly detection**:
  - Amount anomalies: transactions exceeding 3× the per-account median.
  - Currency anomalies: known domestic merchants charged in USD.
- **LLM merchant categorization** using Google Gemini (`gemini-1.5-flash`) with
  retry/backoff and graceful failure handling.
- **Summary generation**: total INR/USD spend, top merchants, anomaly count,
  risk level and an AI narrative (degrades to a computed narrative if the LLM is
  unavailable).
- **Job status tracking** with timestamps and error capture.
- **REST API** for job status, job listing, transactions (with anomaly filter)
  and summaries.
- **Alembic migrations** for schema management.
- **Dockerized** stack (FastAPI, PostgreSQL, Redis, Celery worker).
- **Pytest** test suite.

---

## Setup Instructions

### Option A — Docker (recommended)

Prerequisites: Docker + Docker Compose.

```bash
cp .env.example .env          # then edit GEMINI_API_KEY
docker compose up --build
```

The web service automatically runs `alembic upgrade head` before starting.

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### Option B — Local (without Docker)

Prerequisites: Python 3.12, a running PostgreSQL and Redis.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # point DATABASE_URL / REDIS_URL at your local services
# e.g. DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/transactions
#      REDIS_URL=redis://localhost:6379/0

alembic upgrade head               # create the schema

# Terminal 1 — API
uvicorn app.main:app --reload

# Terminal 2 — Celery worker
celery -A app.workers.celery_app:celery worker --loglevel=info
```

---

## Environment Variables

| Variable          | Description                                            | Example                                                            |
| ----------------- | ------------------------------------------------------ | ----------------------------------------------------------------- |
| `DATABASE_URL`    | SQLAlchemy/psycopg2 PostgreSQL URL                     | `postgresql+psycopg2://postgres:postgres@db:5432/transactions`    |
| `REDIS_URL`       | Celery broker + result backend                         | `redis://redis:6379/0`                                            |
| `GEMINI_API_KEY`  | Google Gemini API key (for categorization & narrative) | `AIza...`                                                          |
| `UPLOAD_DIR`      | Directory for uploaded CSVs (default `uploads`)        | `uploads`                                                          |
| `POSTGRES_USER`   | Postgres user (docker-compose `db` service)            | `postgres`                                                        |
| `POSTGRES_PASSWORD` | Postgres password (docker-compose `db` service)      | `postgres`                                                        |
| `POSTGRES_DB`     | Postgres database name (docker-compose `db` service)   | `transactions`                                                    |

> If `GEMINI_API_KEY` is not set, the pipeline still completes: merchant
> categorization is skipped (`llm_failed=true`) and the summary uses a computed
> narrative instead of an AI-generated one.

---

## Docker Usage

```bash
docker compose up --build          # build and start db, redis, web, worker
docker compose up -d               # detached
docker compose logs -f web worker  # tail logs
docker compose down                # stop
docker compose down -v             # stop and wipe volumes (db + uploads)
```

Services:

| Service  | Description                                  | Port |
| -------- | -------------------------------------------- | ---- |
| `web`    | FastAPI API (runs migrations on startup)     | 8000 |
| `worker` | Celery worker processing CSV jobs            | —    |
| `db`     | PostgreSQL 16                                 | 5432 |
| `redis`  | Redis 7 (Celery broker/backend)              | 6379 |

---

## API Endpoints

Base path: `/jobs`

| Method | Path                                   | Description                                        |
| ------ | -------------------------------------- | -------------------------------------------------- |
| GET    | `/`                                    | Root message                                       |
| GET    | `/health`                              | Health check                                       |
| POST   | `/jobs/upload`                         | Upload a CSV, returns `{job_id, status}`           |
| GET    | `/jobs`                                | List all jobs (newest first)                       |
| GET    | `/jobs/{job_id}`                       | Job detail (status, row counts, timestamps, error) |
| GET    | `/jobs/{job_id}/status`                | Lightweight job status                             |
| GET    | `/jobs/{job_id}/transactions`          | Transactions for a job                             |
| GET    | `/jobs/{job_id}/transactions?anomalies_only=true` | Only anomalous transactions             |
| GET    | `/jobs/{job_id}/summary`               | Job summary (404 until processing completes)       |

### Example

```bash
# Upload
curl -F "file=@samples/transactions_sample.csv;type=text/csv" \
     http://localhost:8000/jobs/upload
# {"job_id":1,"status":"pending"}

# Poll status
curl http://localhost:8000/jobs/1/status
# {"job_id":1,"status":"COMPLETED"}

# Fetch results
curl http://localhost:8000/jobs/1/transactions
curl "http://localhost:8000/jobs/1/transactions?anomalies_only=true"
curl http://localhost:8000/jobs/1/summary
```

A sample CSV is provided at [`samples/transactions_sample.csv`](samples/transactions_sample.csv).

### Expected CSV format

```
txn_id,date,merchant,amount,currency,status,category,account_id
```

`amount` may contain currency symbols/text (e.g. `INR 250.50`) — they are
stripped during cleaning. `category` may be blank (filled as `Uncategorised`
and later enriched by the LLM).

---

## Running Celery

```bash
celery -A app.workers.celery_app:celery worker --loglevel=info
```

Under Docker this runs automatically as the `worker` service. The single task
`app.workers.tasks.process_csv_job` runs the full pipeline for an uploaded job.

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests use an in-memory SQLite database and mock external dependencies (Celery
dispatch and Gemini calls), so **no Postgres, Redis or Gemini key is required**
to run them.

---

## Database Models

- **`jobs`** — one row per upload: `filename`, `status`, `row_count_raw`,
  `row_count_clean`, `created_at`, `completed_at`, `error_message`, `file_path`.
- **`transactions`** — cleaned transactions (FK `job_id`): standard transaction
  fields plus `is_anomaly`, `anomaly_reason`, `llm_category`,
  `llm_raw_response`, `llm_failed`.
- **`job_summaries`** — one summary per job (FK `job_id`): `total_spend_inr`,
  `total_spend_usd`, `top_merchants`, `anomaly_count`, `narrative`,
  `risk_level`.

Relationships: `job.transactions` (1‑to‑many) and `job.summary` (1‑to‑1), both
with cascade delete.

---

## Migrations

Alembic is the source of truth for the schema.

```bash
alembic upgrade head                       # apply migrations
alembic revision --autogenerate -m "msg"   # create a new migration after model changes
alembic downgrade -1                       # roll back one revision
```

`migrations/env.py` reads `DATABASE_URL` from the application config, so the
same environment variable drives the app and the migrations.

---

## Assumptions

- Uploaded files are valid CSVs containing the columns listed above; the
  `account_id`, `amount`, `merchant` and `currency` columns are required for
  anomaly detection.
- "Domestic merchants" for currency-anomaly detection are a fixed list
  (Swiggy, Ola, IRCTC, Zomato, BigBasket).
- An amount is anomalous if it exceeds **3×** the median amount for its account.
- Risk level is derived from anomaly count: `0 → low`, `1–5 → medium`,
  `>5 → high`.
- `top_merchants` is stored as a stringified list (kept from the original
  schema for compatibility).
- Amounts are summed per currency without FX conversion; INR and USD totals are
  reported separately.

## Design Decisions

- **Async processing** keeps uploads fast and decouples ingestion from the
  potentially slow LLM calls (Celery + Redis).
- **Graceful LLM degradation**: a Gemini outage or missing key marks a
  transaction `llm_failed` and falls back to a computed narrative instead of
  failing the whole job, so the locally-computed analytics are never lost.
- **Lazy Gemini initialization** lets the app and tests import cleanly without a
  configured API key.
- **Alembic over `create_all`** for reproducible, versioned schema changes; the
  web container runs `alembic upgrade head` on startup.
- **Type normalization** (`numpy`→native Python) before persistence so psycopg2
  can adapt pandas-derived values.
- **Shared `uploads` volume** between `web` and `worker` so the worker can read
  files the API wrote.

---

## Remaining Risks / Notes

- `google-generativeai` is deprecated upstream in favor of `google-genai`;
  migrating SDKs is out of scope for this assignment but worth tracking.
- Pipeline processing is synchronous within a single Celery task; very large
  CSVs would benefit from chunked/batched processing.
- `top_merchants` is persisted as a string; a JSON column would be cleaner for
  programmatic consumption.
