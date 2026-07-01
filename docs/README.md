# LookOwl Backend — Documentation

LookOwl is the backend service for a **library catalog and management system**. It exposes a REST API (built on FastAPI) that lets client applications register and search books, manage users, and authenticate via JWT bearer tokens. The system is being extended to support physical book copies (`ejemplares`) and loans (`prestamos`).

This folder contains the reference documentation requested by the QA team.

## Contents

| Document | Purpose |
| --- | --- |
| [endpoints.md](./endpoints.md) | Full reference of every implemented HTTP endpoint: routes, parameters, request/response payloads, status codes. |
| [dtos.md](./dtos.md) | Reference of every DTO (request body schema) plus the shared validator types. |
| [deployment.md](./deployment.md) | How the project is built and deployed with Docker Compose (Postgres + migrations + FastAPI app). |

## Tech stack

- **Language / runtime:** Python 3.13
- **Web framework:** FastAPI (`fastapi[standard]` ≥ 0.136)
- **Validation:** Pydantic v2
- **ORM:** SQLAlchemy 2.x
- **Migrations:** Alembic
- **Database:** PostgreSQL 18 (Docker), SQLite in-memory for tests
- **Auth:** JWT (HS256) via `pyjwt`, password hashing with `bcrypt`
- **Package management:** `uv` (lockfile `uv.lock`)

## High-level architecture

The codebase follows a layered structure:

```
api/             FastAPI routers (controllers) + Pydantic DTOs
  controllers/   Endpoint definitions
  dtos/          Request/response models
core/            Cross-cutting concerns: security, validators, exceptions
domain/          Pure domain dataclasses + enums
services/        Business logic, orchestrates repositories
repositories/    Persistence layer (SQLAlchemy)
db/              SQLAlchemy models (ORM) and DB connection
migrations/      Alembic migration scripts
tests/           Pytest suite
```

The app entry point is `main.py`, which mounts both routers under the `/api` prefix:

- `/api/books` — book catalog operations
- `/api/users` — auth (login / register)

## Base URL

- Local (Docker Compose): `http://localhost:8000`
- All endpoints documented in [endpoints.md](./endpoints.md) are prefixed with `/api`.

## Authentication

Most write operations require a JWT bearer token obtained from `POST /api/users/login`. Pass it on subsequent requests as:

```
Authorization: Bearer <token>
```

Tokens expire 30 minutes after issue. See [endpoints.md](./endpoints.md#authentication) for details.
