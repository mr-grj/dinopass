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
- Per-password backup status tracked in the database, visible in the UI
- One-command setup with Docker

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL 16 |
| Frontend | React 18, MUI v6, easy-peasy |
| Package manager | uv (backend), npm (frontend) |
| Infrastructure | Docker, docker-compose |

## Security model

- Master password is hashed with **bcrypt**: not stored in plain or reversibly
- All passwords are encrypted with **Fernet** (symmetric AES) using a key derived via **PBKDF2-HMAC-SHA256** (600,000 iterations) from the master password and a unique random salt
- The derived key lives only in your browser session (`sessionStorage`) and is never persisted server-side: closing the tab clears it automatically
- Updating the master password re-encrypts every stored password transparently

## Running locally

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/)

### 1. Configure the database

Copy the env template and fill in your values:

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

### 2. Start everything

```shell
docker compose up --build
```

That's it. Docker will:
1. Start PostgreSQL and wait for it to be healthy
2. Build and start the FastAPI backend on `http://localhost:8000`
3. Build and serve the React frontend on `http://localhost:3000`

### 3. Open the app

Go to [http://localhost:3000](http://localhost:3000), set a master password, and start adding passwords.

The API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Stopping

```shell
docker compose down
```

To also wipe the database volume:

```shell
docker compose down -v
```

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
