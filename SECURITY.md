# Security

Dinopass is a self-hosted password manager, so getting security right matters. If you find a vulnerability, please report it responsibly rather than opening a public issue.

## Reporting a vulnerability

Open a [GitHub Security Advisory](https://github.com/mrgrj/dinopass/security/advisories/new) (private by default) and describe:

- What the vulnerability is
- How to reproduce it
- What impact you think it has

I'll acknowledge it within a few days and aim to ship a fix or mitigation quickly. I'll credit you in the release notes unless you'd prefer to stay anonymous.

## Scope

Things that are in scope:

- Authentication or session bypass
- Encryption weaknesses or key leakage
- Privilege escalation
- Injection (SQL, command, etc.)
- Anything that could expose stored passwords to an unauthorized party

Things that are out of scope:

- Vulnerabilities that require physical access to the machine running the instance
- Issues in third-party dependencies that don't directly affect dinopass (please report those upstream)
- Self-XSS or issues only exploitable by someone already logged in with their own master password

## Security model

Dinopass is designed to be run on a trusted machine you control. It is **not** designed to be exposed directly to the internet without a reverse proxy, firewall rules, and HTTPS. See the README for deployment guidance.
