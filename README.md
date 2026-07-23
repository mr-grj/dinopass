<div align="center">

# CipherMoth

**Your secrets stay in the dark.**

A simple, self-hosted password manager with **no accounts, no cloud, and no witnesses.**

[![CI](https://github.com/mr-grj/ciphermoth/actions/workflows/ci.yml/badge.svg)](https://github.com/mr-grj/ciphermoth/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/mr-grj/ciphermoth?color=000000&label=release)](https://github.com/mr-grj/ciphermoth/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-000000.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.13-000000.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/postgres-16-000000.svg)](https://www.postgresql.org/)
[![Self-hosted](https://img.shields.io/badge/self--hosted-7dd3c0.svg?labelColor=000000)](#get-started)

</div>

---

## What is this?

I built this for myself because I was tired of every password manager wanting my email address, a subscription, a
browser extension with access to everything, and ideally my soul too. Most of the big ones lean on a hosted account,
a sync layer, or a monthly bill by default.

I wanted something that lives on my own machine, has no telemetry, talks to no third party, and doesn't wake up one day
to announce it's been acquired and migrating to some new platform. No Google. No OAuth. No analytics pinging home. Nothing.

So there's **CipherMoth**. It lives on your hardware, speaks to nobody, and keeps the passwords encrypted with a key only
you know. One master password unlocks everything. If someone gets the database, they get encrypted blobs, not your passwords.

## Screenshots

|  |  |
|---|---|
| **First run: set up your master password** | **The vault** |
| ![Set up your vault](docs/screenshots/00-login.png) | ![Vault overview](docs/screenshots/01-vault.png) |
| **Add a password, generate a strong one** | **Vault health, computed on your device** |
| ![Add password with generator](docs/screenshots/02-add-generator.png) | ![Vault health report](docs/screenshots/03-health.png) |

## Get started

CipherMoth runs on your own machine with [Docker](https://docs.docker.com/get-docker/). One command sets a strong database password, pulls
the **signed** images, and starts everything:

```shell
curl -fsSL https://raw.githubusercontent.com/mr-grj/ciphermoth/master/install.sh | sh
```

Open **[http://localhost:3001](http://localhost:3001)**, create your master password, and you're in. The vault
lives in a persistent Docker volume, so it survives restarts and updates.

Rather read the script before piping it to a shell, set it up by hand, run it on a real server, or tweak the config?
That's all in **[CONTRIBUTING.md](./CONTRIBUTING.md)**.

> ⚠️ **There is no password recovery.** Losing your master password means losing your vault, permanently. No reset link,
> no support email, no backdoor. That's the trade for nobody-but-you holding the key. **Write it down somewhere safe**,
> and take a backup once you've added a few entries.

## What it does

- one master password unlocks the vault, no account, no email, no recovery codes sent to a phone number you changed three years ago
- all passwords encrypted at rest; the key is derived from the master password and never touches the server
- store a username, website, tags, folders, a two-factor (TOTP) secret, and your own custom fields alongside each entry, all encrypted
- built-in two-factor: paste a 2FA secret, and CipherMoth shows the live rolling code, computed in the browser
- secure notes for free-form secrets (recovery codes, Wi-Fi, passport details), encrypted just like passwords
- attach files to any entry (recovery-code PDFs, license keys, key files), up to 5 MB each, encrypted with your vault key
- search, favorites, folders, tags, and password history to keep a growing vault tidy
- trash for deletions you can restore from or empty for good when you're sure
- light and dark themes that flip across the whole app, toggled by a moth that flutters off as the colours fade (and remembers your pick)
- vault health check that flags weak, reused, and old passwords, entirely on your device
- cryptographically secure password generator (not the `Math.random()` kind) with a strength indicator on every entry
- import from Chrome, Bitwarden, KeePass, Proton Pass, and friends via CSV, or restore an encrypted CipherMoth backup
- encrypted backup export, a CLI (`ciphermoth`) for the terminal, and auto-lock plus clipboard-clearing (for the small things that matter ^^)
- notices new releases and can update itself, opt-in and signature-verified (Sigstore / cosign)

## Who it's for (and who it isn't)

CipherMoth is probably a good fit if you:

- want a self-hosted password manager with no accounts, no telemetry, and no third parties
- are comfortable running Docker on a machine you control
- like small, auditable software and are happy owning your own backups

It's probably not for you (yet) if you need browser autofill, a mobile app, family or team sharing, managed cloud sync,
or a way to recover your vault if you forget your master password. No hard feelings, those are real needs, just not what
this is trying to be.

## Security

Straight up, because this is a password manager and you deserve it: **CipherMoth has not been independently audited.**
It's a personal project I use myself and built carefully, with the crypto kept small and readable on purpose, but it has
not been through a formal third-party security review. It's designed for self-hosted personal use on hardware you trust,
not as a public, multi-tenant service holding other people's secrets. Weigh that accordingly.

How it works:

- your master password is hashed with **bcrypt**, never stored in plain; new vaults require a reasonably strong
  one (12+ characters, mixed types), enforced on the server;
- every stored field is encrypted with **Fernet** (AES-128-CBC + HMAC-SHA256) using a key derived from your master
  password via **Argon2id** (OWASP 2024 interactive profile), unique per vault thanks to a random salt;
- even the metadata (websites, 2FA secrets, tags, custom fields, history, attachments) is encrypted; the database never
  learns which sites you have or how you organize them;
- that derived key lives only in your browser's `sessionStorage`, never touches the server, and disappears the moment
  you close the tab
- the password generator uses `crypto.getRandomValues` with rejection sampling, no `Math.random()`, no shortcuts;

**It protects against** someone who steals the database or disk (they get ciphertext and a bcrypt hash), accidental
server-side exposure (the server never persists the master password or the derived key), and casual inspection of
stored data.

**It does not protect against** malware or a keylogger on the device you unlock from, a weak master password, exposing
the instance on the public internet without `https`, or forgetting your master password (there is no recovery). Run it
on a machine and network you trust, use a strong master password, and keep a backup.

To report a vulnerability, see [SECURITY.md](./SECURITY.md).

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, asyncpg |
| Database | PostgreSQL 16 |
| Frontend | React 19, Vite, MUI v9, easy-peasy |
| Package manager | uv (backend), npm (frontend) |
| Infrastructure | Docker, Docker Compose v2 |

## Docs

- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - hacking on CipherMoth, self-hosting on a server, configuration, and updates
- **[docs/CLI.md](./docs/CLI.md)** - the `ciphermoth` command-line reference
- **[SECURITY.md](./SECURITY.md)** - reporting a vulnerability
- Logo, wordmark, and favicon live in [`docs/brand/`](./docs/brand)

## License

MIT: see [LICENSE](./LICENSE).
