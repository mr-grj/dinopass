# Changelog

## [Unreleased]

## [1.1.0] - 2026-07-11

### Added

- **Update notifications.** CipherMoth now tells you when a newer release exists. The check runs entirely in your **browser** against GitHub's public API - the server never phones home - and can be switched off in Settings ("Check for updates") to keep an instance fully third-party-free.
- **One-click updates (opt-in).** An optional `updater` sidecar lets you upgrade from the in-app "Update" button: it pulls the new images, restarts, and runs migrations for you. It's **off by default**; enable it with `make prod-up-autoupdate` (or `docker compose -f docker-compose.prod.yml --profile autoupdate up -d`). Without it, the app still notifies you and shows the exact command to run.

### Security

- **Release images are now signed with cosign** (keyless / Sigstore, via GitHub OIDC). Every published `ciphermoth-{backend,frontend,updater}` image is signed by digest.
- **The self-updater verifies signatures before applying.** It pulls the target images, checks each digest was signed by the official release workflow's identity, and **refuses to run anything that fails verification** - so a compromised registry alone can't push a malicious build to your vault. It also snapshots the database before migrating and **auto-rolls-back** if the new version fails its health check. The privileged (Docker-socket) container has **no network listener**; it's driven only by a file the backend drops after an unlocked-vault, rate-limited request.

## [1.0.0] - 2026-07-11

### Changed

- **Renamed the project to CipherMoth** ("Your secrets stay in the dark."). Everything the app does is unchanged; this is a full rebrand of the name, UI theme, CLI (`ciphermoth`), Docker Compose projects, and GHCR images (`ghcr.io/mr-grj/ciphermoth-{backend,frontend}`). The per-request key header is now `x-ciphermoth-key-derivation` and backup archives contain `ciphermoth_backup.json`, so a backup taken before the rename must be restored before upgrading (or just re-export after).
- **New black-and-glow UI theme.** A minimal dark palette with a teal "glow" accent (`#7dd3c0`) and a moth mark replaces the old black-and-white dino look. Fonts are Space Grotesk + Space Mono, self-hosted (no Google Fonts CDN, in keeping with "talks to nobody"). Login, setup, and the initial unlock are now full-screen dark screens.
- **Simplified to one local stack + prebuilt prod.** Local development now runs a single build-from-source, hot-reload stack on `:3000`/`:8000` (`make dev`); the real vault runs from prebuilt GHCR images via `docker-compose.prod.yml` (`make prod-up`). The separate `:3100`/`:8100` dev stack and the build-from-source `make buildup` path are gone.

## [0.3.0] - 2026-07-10

### Added

- **Website, two-factor, tags and favorites per entry.** Each password can now carry a website, a TOTP secret, tags, and a favorite flag. All of them (except the favorite flag) are encrypted at rest with the same vault key, so the database still only ever holds ciphertext.
- **Built-in two-factor codes.** Paste a base32 secret or an `otpauth://` link and Dinopass shows the live rolling code, computed in your browser (and in the CLI via `password get`).
- **Password history.** When you change a password, the previous value is kept (encrypted, last 10) and can be revealed or copied from the edit dialog.
- **Vault health check.** A local, offline report that flags weak, reused, and stale passwords. It never sends anything anywhere.
- **CSV import from other managers.** Import a plain CSV exported from Chrome, Bitwarden, KeePass, Proton Pass and similar, from the web UI or `dinopass import-csv`. Columns are matched automatically.
- **`make setup`** generates `backend/.db.env` with a strong random database password so first-time setup is one command.
- **Separate personal and development stacks.** `make buildup` (your real vault) and `make dev` now run as distinct Docker Compose projects, each with its own database volume, network, and ports (dev on `3100`/`8100`), so you can run both at once and a dev sandbox can never see or clobber your real vault. `make clean` only ever wipes the dev database; tearing down the real vault is a separate, confirmation-guarded `make clean-prod`. New `make down`/`make dev-down` stop a stack without wiping its data.
- **Environment badge in the app bar.** The dev stack shows a loud amber **DEV** chip (plus an amber accent line); your real vault shows a calm **LIVE** chip. It's derived from the build itself (Vite dev server vs `vite build`), so there's nothing to configure - and it makes it hard to ever mistake the sandbox for the real thing.
- **Prebuilt images + a pull-and-run compose.** Release images are published to GHCR (`ghcr.io/mr-grj/dinopass-backend` and `-frontend`, multi-arch amd64/arm64) whenever a `v*.*.*` tag is pushed. A new `docker-compose.prod.yml` + `.env.prod.example` let you run Dinopass without cloning or building - grab the two files, set a database password, `docker compose -f docker-compose.prod.yml up -d`. The frontend image takes its API URL at container start, so one image works for any host.

### Security

- **Master password strength is now enforced on the server** (at least 12 characters and two character classes) when creating a vault or changing the master password, not just in the browser.

- **Full master password is now authenticated.** bcrypt truncates at 72 bytes, so a very long master password used to only be checked by its first 72 bytes. It's now pre-hashed with SHA-256 before bcrypt so the whole thing counts. This changes the stored hash format and is not backward compatible, so a vault created before this change needs to be set up again.
- **Rate-limited the master password change endpoint.** It verifies the current master password, so leaving it unlimited was a brute-force gap that bypassed the cap on the login check. It's now capped at 10/hour like the check endpoint.
- **Import rejects oversized uploads before reading them** into memory, and the reverse-proxy rate-limiting caveat is now documented in the README.

### Docs

- **README rework, with screenshots.** Added screenshots of the vault, the add/generate flow, the health report, and first-run setup; a "who it's for (and who it isn't)"; a "security status" note that says plainly it hasn't been independently audited; a threat model; and a clearer split between running Dinopass for real vs. developing on it. The full CLI reference moved into [`docs/CLI.md`](docs/CLI.md).

### Internal

- **Backend refactor** - moved exception translation to app-level handlers (endpoints no longer carry `@handle_*` decorator stacks), extracted the per-request key derivation into a FastAPI dependency so the CRUD layer only sees a plain string, simplified the dependency wiring with `Annotated` providers, and fixed the import path's N+1 lookups. No change to the API contract.
- **Fixed long-standing inconsistencies** - the CLI now sends the `username` field on create/update, the API version reads from package metadata instead of a hardcoded string, and the settings defaults live in one place.
- **Frontend refactor** - broke the 1,100-line `PasswordsPage` into a thin container plus focused pieces under `components/vault/` (form, generator, backup, import, empty state, column defs), extracted the secure generator and strength scoring into `src/lib/`, and added a shared `PasswordField` and `useClipboard` hook. No behavior or UI changes - just cleaner, DRYer, easier to follow.
- **Unified password-strength logic** - the vault (5-level) and login (4-level) scales now share one module (`src/lib/passwordStrength.js`) instead of two divergent copies.
- **ESLint 9** - added a flat-config ESLint setup (react-hooks + react-refresh) wired into `make lint`/`make check` and CI. `npm run lint` is clean; the frontend still installs with 0 vulnerabilities.

## [0.2.0] - 2026-03-15

First public release. I've been using this daily for a while and it hasn't eaten any passwords, so here we are.

### What's in it

- **Vault UI** - create, edit, delete, and search passwords from a single page. Search works across name, username, and description so you don't have to remember exactly what you called something
- **Username / email field** - because some sites want a username, some want an email, and some want both for reasons nobody has ever explained
- **Password generator** - configurable length (8-64) and character sets; uses `crypto.getRandomValues` with rejection sampling so the randomness is actually random, not "looks random enough"
- **Password strength indicator** - shows up in the form as you type and as an icon in the vault table, so you can feel appropriately judged by your old passwords
- **Encrypted backup** - exports everything as an AES-256 ZIP protected by your master password. Keep it somewhere safe
- **Backup import** - restore from a backup ZIP with skip or overwrite for conflicts
- **CLI** (`dinopass`) - full vault access from the terminal for when you can't be bothered to open a browser
- **Inactivity lock** - session clears itself after you've walked away; configurable how long it waits
- **Clipboard auto-clear** - copied passwords are wiped from the clipboard after a timeout, because paste history is a thing that exists
- **Settings page** - all the timeouts and delays are configurable from the UI, not hardcoded
- **Rate limiting** - all API routes are rate-limited so someone can't just hammer the login endpoint forever

### Security foundations

- Master password hashed with **bcrypt** - not stored, not reversible
- Passwords encrypted with **Fernet** (AES-128-CBC + HMAC-SHA256) using keys derived via **Argon2id** (64 MiB, 3 iterations, 4 lanes)
- Derived key lives only in `sessionStorage` for the duration of the session - the server never sees it
- Password generator uses `crypto.getRandomValues` with rejection sampling to eliminate modulo bias - the kind of detail that doesn't matter until it does
