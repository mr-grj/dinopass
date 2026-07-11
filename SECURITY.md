# Security

This is a password manager. Security isn't a feature here - it's the whole point. If you find something wrong, please don't open a public issue about it. Tell me privately first.

## Found something? Tell me here

Open a [GitHub Security Advisory](https://github.com/mr-grj/ciphermoth/security/advisories/new) - it's private by default, only visible to you and me. Describe what you found, how to reproduce it, and what you think the impact is. That's all I need to get started.

I'll acknowledge it within a few days. If it's real, I'll fix it and credit you in the release notes - unless you'd rather stay anonymous, which is also fine.

## What I actually care about

Things I want to know about:

- Anything that lets someone read passwords they shouldn't be able to
- Authentication or session bypass
- Encryption weaknesses or key leakage
- SQL injection, command injection, that whole family
- Anything that could expose the vault to an unauthorized party

Things that are out of scope:

- Attacks that require physical access to the machine running the instance - if someone has that, it's already over
- Vulnerabilities in third-party dependencies that don't directly affect ciphermoth - please report those upstream
- Self-XSS or anything only exploitable by someone already authenticated with their own master password

## Updates and the supply chain

Release images (`ciphermoth-backend`, `-frontend`, `-updater`) are signed with [cosign](https://github.com/sigstore/cosign) - keyless, via GitHub OIDC - so each image's digest is provably built by CipherMoth's own release workflow.

The **opt-in** one-click updater (the `autoupdate` compose profile) verifies those signatures against that workflow identity *before* it will run any image, and refuses anything that fails. It snapshots the database before migrating and rolls back automatically on a failed health check. The container that holds the Docker socket has **no network listener** - it acts only on a file the backend writes after an unlocked-vault, rate-limited request. If you'd rather not grant that privilege at all, leave the profile off and update by hand; the app will just show you the command.

If you fork CipherMoth and publish your own images, override `COSIGN_IDENTITY_REGEXP` (and `COSIGN_OIDC_ISSUER`) on the `updater` service so it trusts *your* release workflow, not upstream's.

## One thing worth knowing

CipherMoth is built to run on a machine you trust and control - your home server, a VPS behind a firewall, a Raspberry Pi in your closet. It is not built to sit directly on the open internet without a reverse proxy, HTTPS, and some thought about who can reach it. If you're deploying it that way, the README has guidance. If something goes wrong because it was exposed without those precautions, that's a configuration problem, not a vulnerability.
