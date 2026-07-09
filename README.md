# 🦖 Dinopass

[![CI](https://github.com/mr-grj/dinopass/actions/workflows/ci.yml/badge.svg)](https://github.com/mr-grj/dinopass/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-000000.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.13-000000.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/postgres-16-000000.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-compose-000000.svg)](https://docs.docker.com/compose/)

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

I built this for myself because I was tired of every password manager wanting my email address, a subscription, a browser extension with access to everything, and ideally my soul too. Most of the big ones lean on a hosted account, a sync layer, or a monthly bill by default. Some are open source or can be self-hosted, which is genuinely great, but the easy path still points at a cloud you don't run.

I just wanted something that lives on my own machine, has no telemetry, talks to no third party, and doesn't wake up one day to announce it's been acquired and my vault is migrating to some new platform. No Google. No OAuth. No "sign in with Apple". No analytics pinging home. Nothing.

So I built Dinopass. It's a password manager that lives on your hardware, speaks to nobody, and keeps your passwords encrypted with a key only you know. One master password unlocks everything. If someone gets the database, they get encrypted blobs - not your passwords.

It's probably overkill for most people. But it's mine, and that's kind of the point.

## Screenshots

|  |  |
|---|---|
| **Your vault** | **Add a password, generate a strong one** |
| ![Vault overview](docs/screenshots/01-vault.png) | ![Add password with generator](docs/screenshots/02-add-generator.png) |
| **Vault health, computed on your device** | **First run: set up your master password** |
| ![Vault health report](docs/screenshots/03-health.png) | ![Set up your vault](docs/screenshots/00-login.png) |

Minimal black-and-white UI, a friendly dino, and a live 2FA column that rolls in your browser. That's the whole vibe.

## What it does

The basics you'd expect:

- One master password unlocks the vault - no account, no email, no recovery codes sent to a phone number you changed three years ago
- All passwords encrypted at rest; the encryption key is derived from your master password and never touches the server
- Web UI for day-to-day use: create, edit, delete, search by name, username, website, or tag
- Store the website, a username, tags, and a two-factor (TOTP) secret alongside each password
- Built-in two-factor codes: paste a 2FA secret and Dinopass shows the live rolling code, computed in your browser
- Favorites and tags to keep a growing vault tidy, plus password history so a changed password is never truly gone
- Vault health check that flags weak, reused, and old passwords - runs entirely on your device, nothing is sent anywhere
- Password generator with configurable length and character sets - cryptographically secure, not the `Math.random()` kind
- Strength indicator on every password so you can see at a glance which ones are embarrassing
- CLI (`dinopass`) for when you'd rather not open a browser
- Import from Chrome, Bitwarden, KeePass, Proton Pass and friends with a plain CSV, or restore an encrypted Dinopass backup
- Encrypted backup export and import so you're not one disk failure away from losing everything
- Auto-locks after inactivity and clears the clipboard after copy - small things that matter

## Who it's for (and who it isn't)

Dinopass is probably a good fit if you:

- want a self-hosted password manager with no accounts, no telemetry, and no third parties
- are comfortable running Docker on a machine you control
- like small, auditable software and are happy owning your own backups

It's probably not for you (yet) if you need:

- browser autofill or a mobile app
- family or team sharing
- managed cloud sync across all your devices
- a way to recover your vault if you forget your master password

No hard feelings - those are real needs, just not what this is trying to be.

## Security status

Straight up, because this is a password manager and you deserve it: **Dinopass has not been independently audited.** It's a personal project I use myself and built carefully, with the crypto kept small and readable on purpose - but it has not been through a formal third-party security review. It's designed for self-hosted personal use on hardware you trust, not as a public, multi-tenant service holding other people's secrets. If you're storing high-value secrets, weigh that accordingly.

How to report something is in [SECURITY.md](./SECURITY.md).

## How the security actually works

I spent more time on this than I care to admit, so here's what's actually happening under the hood:

- Your master password is hashed with **bcrypt** - it's never stored in plain, and nothing is reversible. New vaults require a reasonably strong master password (at least 12 characters, mixed types), enforced on the server, not just in the browser
- Every stored password is encrypted with **Fernet** (AES-128-CBC + HMAC-SHA256) using a key derived from your master password via **Argon2id** (64 MiB memory, 3 iterations, 4 lanes - the OWASP 2024 interactive profile). The key is unique per vault thanks to a random salt
- The website, two-factor secret, tags, and password history are encrypted the same way. The database never learns which sites you have accounts on or how you organise them
- That derived key lives only in your browser's `sessionStorage` for the duration of your session - it never touches the server, and it disappears the moment you close the tab
- If you change your master password, every encrypted field is re-encrypted transparently
- The password generator uses `crypto.getRandomValues` with rejection sampling to eliminate modulo bias - no `Math.random()`, no shortcuts

If someone steals the database, they get a pile of ciphertext and a bcrypt hash. Without your master password - and assuming you chose a strong one - there's nothing in there they can read.

## Threat model

No security tool defends against everything, and a password manager that pretends otherwise is lying to you. Here's the honest shape of it.

**Dinopass is built to protect against:**

- Someone who steals the database or the disk - they get ciphertext and a bcrypt hash, not your passwords
- Accidental server-side exposure - the server never persists your master password or the derived key
- Casual inspection of stored data - even the metadata (websites, tags, 2FA secrets, history) is encrypted, not just the password value

**Dinopass does not protect against:**

- Malware, a keylogger, or a compromised browser on the device you use to unlock the vault
- A malicious script running in your session (a cross-site scripting bug, a poisoned dependency) reading the key while the tab is open - this is the usual trade-off for any web vault, and it's why the dependency list is kept small
- A weak master password - if it's guessable, everything above unwinds
- Exposing the instance directly on the public internet without HTTPS and a reverse proxy
- Forgetting your master password - there is no recovery, full stop (see below)

The takeaway: run it on a machine and network you trust, use a strong master password, and keep a backup.

## Tech stack

Nothing exotic. I used tools I know and trust.

| Layer | Tech |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL 16 |
| Frontend | React 19, Vite, MUI v9, easy-peasy |
| Package manager | uv (backend), npm (frontend) |
| Code style | ruff (backend), Prettier (frontend) |
| Type checking | ty (backend) |
| Infrastructure | Docker, Docker Compose v2 |

## Quick start (personal use)

This is the path if you want to run Dinopass for your **real, everyday passwords**. You need [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/). That's it.

**1. Generate the database config** (creates `backend/.db.env` with a strong random password):

```shell
make setup
```

**2. Build and start your vault:**

```shell
make buildup
```

**3. Open [http://localhost:3000](http://localhost:3000)**, create a master password, and you're in.

Your data lives in a persistent Docker volume, so it survives restarts and updates. When you're done, `make down` stops it without touching your data.

> ⚠️ **There is no password recovery.** Losing your master password means losing your vault - permanently. No reset link, no support email, no backdoor. That's the trade for nobody-but-you holding the key. Write your master password down somewhere safe, and take a backup (from the UI or the CLI) once you've added a few entries.

<details>
<summary>Prefer to configure the database by hand?</summary>

Instead of `make setup`, copy the template and edit it:

```shell
cp backend/.db.env.template backend/.db.env
```

```dotenv
POSTGRES_HOST=db
POSTGRES_DB=dinopass
POSTGRES_USER=youruser
POSTGRES_PASSWORD=a-strong-password   # openssl rand -base64 32
PGDATA=/var/lib/postgresql/data/pgdata
```
</details>

## Personal use vs development

Dinopass runs as **two completely separate stacks** so you can trust one with real passwords and treat the other as a throwaway sandbox. They have different Docker Compose project names, which means separate databases, networks, and ports - you can run both at the same time and the dev sandbox can never see or clobber your real vault.

| | Personal (real vault) | Development |
|---|---|---|
| Start it with | `make buildup` | `make dev` |
| Compose project | `dinopass` | `dinopass-dev` |
| Database volume | `dinopass_postgres_data` (persistent) | `dinopass-dev_postgres_data` (disposable) |
| UI / API | `:3000` / `:8000` | `:3100` / `:8100` |
| Hot-reload | no | yes |
| `make clean` | never touches it | wipes it freely |

> ⚠️ **Never store real passwords in the development stack.** It exists for testing with throwaway data. `make clean` erases the dev database without asking - which is exactly why your real vault lives in a different project that `make clean` never touches. To tear down the real vault you have to run `make clean-prod`, which makes you confirm first.

So you can always tell the two apart at a glance, the app bar carries an environment badge: a loud amber **DEV** chip (with an amber underline) on the development stack, and a calm **LIVE** chip on your real vault. If you ever see amber, you're in the sandbox - don't type anything real.

So the recommended setup for daily use while hacking on the code is simply: `make buildup` once for your real vault, and `make dev` whenever you want to work on Dinopass.

## Development

Want to work on Dinopass itself? Start the dev stack (source-mounted, hot-reload):

```shell
make dev
```

The backend restarts on any `.py` change and the React dev server picks up frontend changes instantly. Dev runs at [http://localhost:3100](http://localhost:3100) (UI) and `http://localhost:8100` (API); the API explorer is at `/docs` on the API port.

All `make` commands run locally, not inside Docker.

| Command | What it does |
|---|---|
| `make setup` | Create `backend/.db.env` with a generated database password |
| `make buildup` | Build and start the **production** stack (your real vault) |
| `make down` | Stop production, keeping its database volume |
| `make clean-prod` | Destroy the production database volume (guarded - asks to confirm) |
| `make dev` | Start the **dev** stack with hot-reload |
| `make dev-down` | Stop the dev stack, keeping its database volume |
| `make clean` | Remove the dev stack + its volume, delete `__pycache__` (never touches prod) |
| `make all` | `clean` then `dev` - a fresh dev sandbox |
| `make lint` | `ruff check` (backend) + ESLint (frontend) |
| `make typecheck` | `ty check` (backend) |
| `make format` | Auto-format backend (ruff) and frontend (Prettier) |
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
| `VITE_API_URL` | `http://localhost:8000/api` | Backend API base URL |

**CLI:**

| Variable | Default | Description |
|---|---|---|
| `DINOPASS_API_URL` | `http://localhost:8000/api` | Backend API base URL |

## Putting it on a real server

Dinopass is built to run on a machine you trust - your home server, a VPS behind a firewall, a Raspberry Pi in your closet - not to sit naked on the open internet. If you're deploying it somewhere reachable:

- Set `CORS_ORIGINS` to your actual domain and enable `DISABLE_DOCS=true`
- Put everything behind a reverse proxy (nginx, Caddy) with HTTPS
- Don't expose Postgres (port `5432`) to the outside world

One thing to know about rate limiting behind a proxy: the limits are keyed on the client IP, which the app reads from the network connection. Behind a reverse proxy every request looks like it comes from the proxy, so the limits become global instead of per client. If you want per-client rate limiting, configure your proxy to preserve the real client address (and only trust `X-Forwarded-For` from the proxy itself).

## CLI

There's a `dinopass` CLI for grabbing a password from the terminal without opening a browser. It's a thin client against the same API, so everything stays encrypted the same way.

```shell
cd backend
uv tool install .
dinopass password list
```

Full command reference, install options, and examples: **[docs/CLI.md](docs/CLI.md)**.

## License

MIT: see [LICENSE](./LICENSE).
