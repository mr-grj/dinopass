# 🦖 Dinopass

> A self-hosted password manager for people who are tired of forgetting passwords (and resetting them, again).

```
               __
              / _)  -- Rawr. Your passwords are safe with me.
     _.----._/ /
    /         /
 __/ (  | (  |
/__.-'|_|--|_|
```

---

## What is this?

Dinopass is a personal, self-hosted password manager. One master password unlocks everything. All stored passwords are encrypted using a key derived from that master password: so even if someone gets the database, they get nothing useful without it.

Built because resetting passwords every other week gets old fast.

## Features

- Single master password to rule them all
- All passwords encrypted at rest with Fernet (AES-128-CBC) via PBKDF2-derived keys
- REST API backend (FastAPI + PostgreSQL)
- Web UI (React + MUI): create, view, edit, delete passwords
- Encrypted backup export: generates an AES-256 password-protected ZIP you can open with your master password
- Backup import: restore passwords from a dinopass backup ZIP, with skip or overwrite conflict strategy
- Per-password backup status tracked in the database, visible in the UI
- One-command setup with Docker

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL 16 |
| Frontend | React 18, MUI v6, easy-peasy |
| Package manager | uv (backend), npm (frontend) |
| Infrastructure | Docker, Docker Compose v2 |

## Security model

- Master password is hashed with **bcrypt**: not stored in plain or reversibly
- All passwords are encrypted with **Fernet** (symmetric AES) using a key derived via **PBKDF2-HMAC-SHA256** (600,000 iterations) from the master password and a unique random salt
- The derived key lives only in your browser session (`sessionStorage`) and is never persisted server-side: closing the tab clears it automatically
- Updating the master password re-encrypts every stored password transparently

## Running locally

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)

### 1. Configure the database

```shell
cp backend/.db.env.template backend/.db.env
```

```dotenv
# backend/.db.env
POSTGRES_HOST=db
POSTGRES_DB=dinopass
POSTGRES_USER=youruser
POSTGRES_PASSWORD=a-strong-password
PGDATA=/var/lib/postgresql/data/pgdata
```

### 2. Start

Two compose files are provided:

| File | Purpose | When to use |
|---|---|---|
| `docker-compose.yml` | Production: optimised multi-stage images, static frontend build | Deploying or testing a production-like build |
| `docker-compose.dev.yml` | Development overlay: source mounts, hot-reload | Actively working on the code |

**Production:**
```shell
make buildup          # build and start in background
# or
docker compose up --build
```

**Development (hot-reload):**
```shell
make dev
# or
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

In dev mode the backend restarts on any `.py` change and the React dev server picks up frontend changes instantly via HMR. No rebuild needed.

Both modes start on the same addresses: `http://localhost:3000` (UI) and `http://localhost:8000` (API). API docs at `http://localhost:8000/docs`.

### Stopping

```shell
docker compose down       # stop containers
docker compose down -v    # stop and wipe the database volume
```

## Development

All `make` commands run **locally** (not inside Docker).

| Command | What it does |
|---|---|
| `make all` | Full clean + rebuild (`clean` then `buildup`) |
| `make buildup` | Build images and start all containers in the background |
| `make dev` | Start with hot-reload (`docker-compose.yml` + `docker-compose.dev.yml`) |
| `make clean` | Stop containers, remove volumes/images, delete `__pycache__` |
| `make lint` | `ruff check`: report linting issues |
| `make format` | `ruff format`: auto-format source files in place |
| `make check` | Lint + format check, no writes (suitable for CI) |

`make lint/format/check` require [uv](https://docs.astral.sh/uv/) with dev deps: `uv sync --group dev` inside `backend/`.

### Database migrations

Schema is managed with **Alembic**. On every startup the backend runs `alembic upgrade head` automatically: no manual steps needed.

To create a migration after changing a model (requires a running database):

```shell
cd backend
uv run alembic revision --autogenerate -m "describe the change"
```

Migration files land in `migrations/dinopass/versions/` and are auto-formatted with ruff.

## Configuration

The backend reads these environment variables (all optional, with sensible defaults):

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |
| `DISABLE_DOCS` | `false` | Set `true` to hide `/docs` and `/redoc` |
| `DEBUG` | `false` | FastAPI debug mode |

The frontend reads:

| Variable | Default | Description |
|---|---|---|
| `REACT_APP_API_URL` | `http://localhost:8000/api` | Backend API base URL |

## License

MIT: see [LICENSE](./LICENSE).
