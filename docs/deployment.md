# Deployment (Docker Compose)

The project is deployed as a Docker Compose stack composed of three services that bring up Postgres, run pending database migrations, and finally start the FastAPI app.

Relevant files:

- `Dockerfile` — multi-stage build for the application image.
- `docker-compose.yml` — orchestration of the database, the one-shot migration job, and the app.
- `.env.docker` — environment variables consumed by the compose stack.
- `.dockerignore` — files excluded from the build context.
- `alembic.ini` + `migrations/` — Alembic configuration and migration scripts.

## Services

| Service | Image / build | Role |
| --- | --- | --- |
| `pos_db` | `postgres:18` (container name `library_database`) | PostgreSQL database. Persists data to the named volume `postgres_data`. Exposes port `5432` on the host. Healthcheck uses `pg_isready`. |
| `migrate` | Built from `./Dockerfile` | One-shot job that runs `alembic upgrade head`. Waits for `pos_db` to be healthy and restarts on failure. |
| `app` | Built from `./Dockerfile` | FastAPI application. Exposes port `8000` on the host. Starts only after `migrate` completes successfully and `pos_db` is healthy. |

All three services read environment variables from `.env.docker`.

## Environment variables

`.env.docker` provides the credentials and connection string used by every service:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=biblioteca
DATABASE_URL=postgresql+psycopg://postgres:postgres@pos_db:5432/biblioteca
```

- `POSTGRES_*` configure the Postgres container.
- `DATABASE_URL` is consumed by SQLAlchemy / Alembic inside the `app` and `migrate` containers. The host `pos_db` resolves to the database container on the Compose network.

> Do **not** commit production secrets to `.env.docker`. For real deployments, override these via your orchestrator's secret store or by mounting a different env file.

## Image build

The `Dockerfile` is a multi-stage build:

1. **Builder stage** (`python:3.13-slim`):
   - Pulls the `uv` binary from `ghcr.io/astral-sh/uv:latest`.
   - Runs `uv sync --frozen --no-dev` against the bind-mounted `pyproject.toml` and `uv.lock` so dependencies are resolved deterministically.
   - Copies the project and re-syncs to install the project itself.
2. **Runtime stage** (`python:3.13-slim`):
   - Creates a non-root user `app`.
   - Copies the prepared `/app` (including the resolved `.venv`) from the builder.
   - Exposes port `8000`.
   - Default command: `fastapi run main.py --host 0.0.0.0 --port 8000`.

## Bring the stack up

From the repository root:

```bash
docker compose up --build
```

What happens:

1. Postgres starts and becomes healthy.
2. `migrate` runs `alembic upgrade head` against the database and exits with status `0`.
3. `app` starts and listens on `http://localhost:8000`.

The API is now reachable at:

- `http://localhost:8000/api/books/`
- `http://localhost:8000/api/users/login`
- `http://localhost:8000/api/users/register`
- `http://localhost:8000/docs` — auto-generated FastAPI Swagger UI.
- `http://localhost:8000/redoc` — ReDoc alternative.

## Common operations

| Action | Command |
| --- | --- |
| Build and start in the background | `docker compose up --build -d` |
| Stop and keep data | `docker compose down` |
| Stop and **delete** Postgres data | `docker compose down -v` |
| Re-run migrations only | `docker compose run --rm migrate` |
| Tail app logs | `docker compose logs -f app` |
| Open a psql shell against the DB | `docker compose exec pos_db psql -U postgres -d biblioteca` |

## QA / smoke-test checklist

1. `docker compose up --build` finishes with `app` listening on `:8000`.
2. `GET http://localhost:8000/docs` renders the Swagger UI.
3. Database tables created by Alembic exist (`libros`, `ejemplares`, `usuarios`, `prestamos`, ...).
4. `POST /api/users/register` succeeds with a valid `RegisterUserDto`.
5. `POST /api/users/login` returns a JWT for those credentials.
6. `POST /api/books/register` with the JWT and a valid `RegisterBookDto` returns `{ "id": <int> }`.
7. `GET /api/books/?limit=10` lists the created book and reports correct pagination.

## Notes & known gotchas

- The Postgres image is `postgres:18` (current at the time of writing). If pulling fails on older Docker daemons, downgrade the tag and update the volume path accordingly.
- The signing secret in `core/security.py` (`SECRET_KEY`) is currently hard-coded. Before any production deploy it should be moved to an environment variable and rotated.
- `core/security.py` token expiry is **30 minutes** (`ACCESS_TOKEN_EXPIRE_MINUTES`). Long-running QA test runs may need to re-login.
- The `migrate` service uses `restart: on-failure`. If a migration is genuinely broken, watch the logs (`docker compose logs migrate`) instead of letting it retry indefinitely.
