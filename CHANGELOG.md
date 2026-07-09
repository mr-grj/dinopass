# Changelog

## [Unreleased]

### Internal

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
