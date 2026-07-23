# Contributing & running it your way

This doc is for people who want to **hack on CipherMoth** or **self-host it their own way**, on a real server, behind a proxy, with custom ports. If you just want to run it on your machine, the [README quick start](./README.md#get-started) is all you need; come back here when you want more.

## Development

Clone the repo, then start the dev stack. It builds from your working tree and hot-reloads, and it's a throwaway sandbox with its own database, completely separate from any real vault.

```shell
make setup   # creates backend/.db.env with a generated database password
make dev     # build + start with hot-reload
```

**Open [http://localhost:3000](http://localhost:3000)** (UI) and `http://localhost:8000` (API); the API explorer is at `/docs` on the API port. The backend restarts on any `.py` change and the React dev server picks up frontend changes instantly.

### Dev sandbox vs the real vault

| | Development (local) | Real vault |
|---|---|---|
| Start it with | `make dev` | `docker compose -f docker-compose.prod.yml up -d` (or `make prod-up`) |
| Source | built from your working tree, hot-reload | prebuilt GHCR images |
| Compose project | `ciphermoth-dev` | `ciphermoth` |
| Database volume | `ciphermoth-dev_postgres_data` (disposable) | `ciphermoth_postgres_data` (persistent) |
| UI / API | `:3000` / `:8000` | `:3000` / `:8000` (configurable) |
| Badge in app bar | amber **DEV** | calm **LIVE** |

They are separate Compose projects with separate volumes, so the dev sandbox can never see or clobber your real vault. The environment badge is derived from the build itself (Vite dev server vs `vite build`), so there's nothing to configure. If you ever see amber, you're in the sandbox, don't type anything real.

> Both default to port `3000`. That's fine because dev is local and the real vault runs on your server. If you ever run both on one host, remap the prod ports with `CIPHERMOTH_FRONTEND_PORT` / `CIPHERMOTH_BACKEND_PORT`.

All `make` commands run locally, not inside Docker.

| Command | What it does |
|---|---|
| `make setup` | Create `backend/.db.env` with a generated database password |
| `make dev` | Build and start the dev stack with hot-reload (UI `:3000`, API `:8000`) |
| `make down` | Stop the dev stack, keeping its database volume |
| `make clean` | Remove the dev stack + its volume, delete `__pycache__` |
| `make all` | `clean` then `dev`, a fresh dev sandbox |
| `make prod-up` | Pull and start the real vault from GHCR images (needs a sibling `.env`) |
| `make prod-down` | Stop the real vault, keeping its database volume |
| `make clean-prod` | Destroy the real vault's database volume (guarded, asks to confirm) |
| `make lint` | `ruff check` (backend) + ESLint (frontend) |
| `make typecheck` | `ty check` (backend) |
| `make format` | Auto-format backend (ruff) and frontend (Prettier) |
| `make check` | Lint + type check + format check, no writes, what CI runs |

`make lint/typecheck/format/check` need [uv](https://docs.astral.sh/uv/) with dev deps (`uv sync --group dev` inside `backend/`) and Node.js with npm deps (`npm install` inside `frontend/`).

### Before you push

Run `make check`. It mirrors CI exactly: `ruff check` + `ruff format --check` + `ty check` on the backend, ESLint + Prettier on the frontend. Keep it green.

### Database migrations

Schema is managed with Alembic. The backend runs `alembic upgrade head` automatically on every startup, so you never need to run migrations by hand.

To create a migration after changing a model (needs a running database):

```shell
cd backend
uv run alembic revision --autogenerate -m "describe the change"
```

Migration files land in `migrations/ciphermoth/versions/`.

## Configuration

Everything is optional, the defaults work fine for local use.

**Backend:**

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |
| `DISABLE_DOCS` | `false` | Set `true` to hide `/docs` and `/redoc` |
| `DEBUG` | `false` | FastAPI debug mode |
| `CIPHERMOTH_RATE_LIMIT` | `100/hour` | Rate limit per route (e.g. `50/hour`, `10/minute`) |

**Frontend:**

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000/api` | Backend API base URL |

**CLI:**

| Variable | Default | Description |
|---|---|---|
| `CIPHERMOTH_API_URL` | `http://localhost:8000/api` | Backend API base URL |

## Putting it on a real server

CipherMoth is built to run on a machine you trust, your home server, a VPS behind a firewall, a Raspberry Pi in your closet, not to sit naked on the open internet. If you're deploying it somewhere reachable:

- Set `CIPHERMOTH_FRONTEND_ORIGIN` / `CORS_ORIGINS` to your actual domain and enable `DISABLE_DOCS=true`
- Put everything behind a reverse proxy (nginx, Caddy) with HTTPS
- Don't expose Postgres (port `5432`) to the outside world

One thing to know about rate limiting behind a proxy: the limits are keyed on the client IP, which the app reads from the network connection. Behind a reverse proxy every request looks like it comes from the proxy, so the limits become global instead of per client. If you want per-client rate limiting, configure your proxy to preserve the real client address (and only trust `X-Forwarded-For` from the proxy itself).

## Staying up to date

CipherMoth notices when a newer release is out and shows an **Update** chip in the app bar. The check runs **in your browser** against GitHub's public API, the server never phones home, and you can turn it off under Settings, "Check for updates", if you'd rather your instance talk to nobody at all.

**Updating by hand** (always available): edit `CIPHERMOTH_VERSION` in your `.env` (or leave it `latest`) and re-run:

```shell
docker compose -f docker-compose.prod.yml pull && \
docker compose -f docker-compose.prod.yml up -d
```

**One-click updates** (opt-in): if you'd like the **Update** button to do this for you, start the stack with the self-updater enabled (the installer offers to do this for you):

```shell
docker compose -f docker-compose.prod.yml --profile autoupdate up -d
# from a repo clone you can also use: make prod-up-autoupdate
```

This adds a small `updater` container that holds the Docker socket. Because it can restart your stack, it's **off by default** and deliberately careful:

- It **verifies every image is signed** (cosign / Sigstore) by CipherMoth's official release workflow before running it, a compromised registry alone can't slip you a malicious build.
- It **snapshots the database** before applying and **rolls back automatically** if the new version fails its health check.
- It has **no network listener**, it only reacts to a file the backend writes after an unlocked-vault, rate-limited request. Your master password is never involved.

If the updater isn't enabled, the button simply shows you the manual command above.
