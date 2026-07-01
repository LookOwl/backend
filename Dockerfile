# syntax=docker/dockerfile:1
# Capa para construccion
FROM python:3.13-slim AS builder

RUN pip install --no-cache-dir uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the source code
COPY . /app

RUN uv sync --frozen --no-dev

# Capa para runtime
FROM python:3.13-slim

RUN groupadd -r app && useradd -r -d /app -g app app

COPY --from=builder --chown=app:app /app /app
COPY --chown=app:app entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"

USER app
WORKDIR /app

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
