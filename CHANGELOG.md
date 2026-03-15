# Changelog

## [0.2.0] - 2026-03-15

### Features

- **Vault UI** - create, edit, delete, and search passwords (by name, username, or description) from a single page
- **Username / email field** - store the login identifier alongside the password
- **Password generator** - configurable length (8–64) and character sets (A–Z, a–z, 0–9, symbols); cryptographically secure with rejection sampling to eliminate modulo bias
- **Password strength indicator** - live strength bar in the form and a per-row icon in the vault table
- **Encrypted backup** - export all passwords as an AES-256 ZIP protected by the master password
- **Backup import** - restore from a dinopass ZIP with skip or overwrite conflict strategy
- **CLI** (`dinopass`) - manage the vault from the terminal: `list`, `get`, `create`, `update`, `delete`, `backup`, `import`
- **Inactivity lock** - session auto-clears after a configurable idle period
- **Clipboard auto-clear** - copied passwords are wiped from the clipboard after a configurable timeout
- **Settings page** - configure inactivity timeout, clipboard clear delay, and more from the UI
- **Rate limiting** - all API routes are rate-limited, configurable via `DINOPASS_RATE_LIMIT`

### Security

- Master password hashed with **bcrypt**
- Passwords encrypted with **Fernet** (AES-128-CBC + HMAC-SHA256) using keys derived via **Argon2id** (64 MiB, 3 iterations, 4 lanes)
- Derived key lives only in `sessionStorage`, never sent to or stored by the server
- Password generator uses `crypto.getRandomValues` with rejection sampling (no modulo bias)
