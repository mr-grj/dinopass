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

I built this for myself because I was tired of every password manager wanting my email address, a subscription, a browser extension with access to everything, and ideally my soul too. 1Password, Bitwarden, LastPass - they all eventually want you to trust some cloud you don't control, run code you can't audit, or pay monthly for the privilege of storing text.

I just wanted something that runs on my own machine, has no telemetry, talks to no third party, and doesn't wake up one day to announce it's been acquired and my vault is migrating to some new platform. No Google. No OAuth. No "sign in with Apple". No analytics pinging home. Nothing.

So I built Dinopass. It's a password manager that lives on your hardware, speaks to nobody, and keeps your passwords encrypted with a key only you know. One master password unlocks everything. If someone gets the database, they get encrypted blobs and nothing else.

It's probably overkill for most people. But it's mine, and that's kind of the point.

## What it does

The basics you'd expect:

- One master password unlocks the vault - no account, no email, no recovery codes sent to a phone number you changed three years ago
- All passwords encrypted at rest; the encryption key is derived from your master password and never touches the server
- Web UI for day-to-day use: create, edit, delete, search passwords by name, username, or description
- Password generator with configurable length and character sets - cryptographically secure, not the `Math.random()` kind
- Strength indicator on every password so you can see at a glance which ones are embarrassing
- CLI (`dinopass`) for when you'd rather not open a browser
- Encrypted backup export and import so you're not one disk failure away from losing everything
- Auto-locks after inactivity and clears the clipboard after copy - small things that matter

## Tech stack

Nothing exotic. I used tools I know and trust.

| Layer | Tech |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL 16 |
| Frontend | React 18, MUI v6, easy-peasy |
| Package manager | uv (backend), npm (frontend) |
| Code style | ruff (backend), Prettier (frontend) |
| Type checking | ty (backend) |
| Infrastructure | Docker, Docker Compose v2 |

## How the security actually works

I spent more time on this than I care to admit, so here's what's actually happening under the hood:

- Your master password is hashed with **bcrypt** - it's never stored in plain, and nothing is reversible
- Every stored password is encrypted with **Fernet** (AES-128-CBC + HMAC-SHA256) using a key derived from your master password via **Argon2id** (64 MiB memory, 3 iterations, 4 lanes - the OWASP 2024 interactive profile). The key is unique per vault thanks to a random salt
- That derived key lives only in your browser's `sessionStorage` for the duration of your session - it never touches the server, and it disappears the moment you close the tab
- If you change your master password, every stored password is re-encrypted transparently
- The password generator uses `crypto.getRandomValues` with rejection sampling to eliminate modulo bias - no `Math.random()`, no shortcuts

If someone steals the database, they have a pile of ciphertext and a bcrypt hash. Without the master password, that's useless.

## Running it

You need [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/). That's it.

### 1. Configure the database

```shell
cp backend/.db.env.template backend/.db.env
```

Edit `backend/.db.env` and set a real username and password:

```dotenv
POSTGRES_HOST=db
POSTGRES_DB=dinopass
POSTGRES_USER=youruser
POSTGRES_PASSWORD=a-strong-password   # openssl rand -base64 32
PGDATA=/var/lib/postgresql/data/pgdata
```

### 2. Start

There are two compose files - one for running it, one for working on it:

| File | Purpose | When to use |
|---|---|---|
| `docker-compose.yml` | Production: optimised multi-stage images, static frontend build | Deploying or testing a production-like build |
| `docker-compose.dev.yml` | Development overlay: source mounts, hot-reload | Actively working on the code |

**Just run it:**
```shell
make buildup
# or: docker compose up --build
```

**Hack on it (hot-reload):**
```shell
make dev
# or: docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

In dev mode the backend restarts on any `.py` change and the React dev server picks up frontend changes instantly. No rebuild needed.

Both modes run at `http://localhost:3000` (UI) and `http://localhost:8000` (API). The API explorer is at `http://localhost:8000/docs` if you want to poke around.

### Stopping

```shell
docker compose down       # stop
docker compose down -v    # stop and wipe the database too
```

## Development

All `make` commands run locally, not inside Docker.

| Command | What it does |
|---|---|
| `make all` | Full clean + rebuild |
| `make buildup` | Build images and start all containers in the background |
| `make dev` | Start with hot-reload |
| `make clean` | Stop containers, remove volumes/images, delete `__pycache__` |
| `make lint` | `ruff check`: report linting issues (backend) |
| `make typecheck` | `ty check`: static type analysis (backend) |
| `make format` | Auto-format backend (ruff) and frontend (Prettier) in place |
| `make check` | Lint + type check + format check, no writes - what CI runs |

`make lint/typecheck/format/check` need [uv](https://docs.astral.sh/uv/) with dev deps (`uv sync --group dev` inside `backend/`) and Node.js with npm deps (`npm install` inside `frontend/`).

### Database migrations

Schema is managed with Alembic. The backend runs `alembic upgrade head` automatically on every startup, so you never need to run migrations by hand.

To create a migration after changing a model (needs a running database):

```shell
cd backend
uv run alembic revision --autogenerate -m "describe the change"
```

Migration files land in `migrations/dinopass/versions/`.

## Configuration

Everything is optional - the defaults work fine for local use.

**Backend:**

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |
| `DISABLE_DOCS` | `false` | Set `true` to hide `/docs` and `/redoc` |
| `DEBUG` | `false` | FastAPI debug mode |
| `DINOPASS_RATE_LIMIT` | `100/hour` | Rate limit per route (e.g. `50/hour`, `10/minute`) |

**Frontend:**

| Variable | Default | Description |
|---|---|---|
| `REACT_APP_API_URL` | `http://localhost:8000/api` | Backend API base URL |

**CLI:**

| Variable | Default | Description |
|---|---|---|
| `DINOPASS_API_URL` | `http://localhost:8000/api` | Backend API base URL |

> **Putting this on a real server?** Set `CORS_ORIGINS` to your actual domain, enable `DISABLE_DOCS=true`, put everything behind a reverse proxy (nginx, Caddy) with HTTPS, and don't expose port `5432` to the outside world. Dinopass is designed to run on a machine you trust - it's not hardened for sitting naked on the internet.

## CLI

Sometimes you just want to grab a password from the terminal without switching windows. That's what the CLI is for.

### Install

```shell
cd backend
uv tool install .
```

Or run it without installing:

```shell
cd backend
uv run dinopass <command>
```

### Commands

```
dinopass password list                     List all passwords
dinopass password get <name>               Reveal a password
dinopass password create <name>            Add a new password (interactive)
dinopass password update <name>            Update value or description (interactive)
dinopass password delete <name>            Delete a password (asks for confirmation)
dinopass backup [--out <dir>]              Export an encrypted backup ZIP
dinopass import <file> [--on-conflict]     Import from a backup ZIP (skip|overwrite)
```

Every command that touches encrypted data prompts for the master password. Use `--help` on any command for details.

### Examples

```shell
# Add a new password
$ dinopass password create github
Master password:
Password value:
Repeat for confirmation:
Description: Personal account
✓  Created github

# Reveal it
$ dinopass password get github
Master password:

  github
  Value        hunter2
  Description  Personal account

# List everything
$ dinopass password list
Master password:
Name      Description       Backed up
github    Personal account  –
gmail     Work email        ✓

# Create an encrypted backup
$ dinopass backup --out ~/backups
Master password:
✓  Backup saved to ~/backups/dinopass_backup_20260314_120000.zip

# Import with overwrite
$ dinopass import dinopass_backup_20260314_120000.zip --on-conflict overwrite
Master password:
✓  Import complete - 3 added, 1 overwritten, 0 skipped
```

## License

MIT: see [LICENSE](./LICENSE).
