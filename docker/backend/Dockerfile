FROM python:3.11-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./

RUN uv sync --frozen --no-install-project --no-group dev


FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src

RUN useradd -ms /bin/bash dinopass

WORKDIR /app/src

COPY --from=builder /app/.venv /app/.venv
COPY backend/ .

USER dinopass

CMD ["uvicorn", "main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "80"]
