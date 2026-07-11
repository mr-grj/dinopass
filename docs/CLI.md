# CipherMoth CLI

Sometimes you just want to grab a password from the terminal without switching windows. That's what the CLI is for. It's a thin client that talks to the same API as the web UI, so everything stays encrypted the same way.

## Install

```shell
cd backend
uv tool install .
```

Or run it without installing:

```shell
cd backend
uv run ciphermoth <command>
```

By default the CLI talks to `http://localhost:8000/api`. Point it somewhere else with the `CIPHERMOTH_API_URL` environment variable.

## Commands

```
ciphermoth password list                     List all passwords
ciphermoth password get <name>               Reveal a password (and its live 2FA code)
ciphermoth password create <name>            Add a new password (interactive)
ciphermoth password update <name>            Update value, website, 2FA or description (interactive)
ciphermoth password delete <name>            Delete a password (asks for confirmation)
ciphermoth backup [--out <dir>]              Export an encrypted backup ZIP
ciphermoth import <file> [--on-conflict]     Import from a CipherMoth backup ZIP (skip|overwrite)
ciphermoth import-csv <file> [--on-conflict] Import a CSV from another manager (skip|overwrite)
```

Every command that touches encrypted data prompts for the master password. Use `--help` on any command for details.

## Examples

```shell
# Add a new password
$ ciphermoth password create github
Master password:
Password value:
Repeat for confirmation:
Description: Personal account
✓  Created github

# Reveal it
$ ciphermoth password get github
Master password:

  github
  Value        hunter2
  Description  Personal account

# List everything
$ ciphermoth password list
Master password:
Name      Description       Backed up
github    Personal account  –
gmail     Work email        ✓

# Create an encrypted backup
$ ciphermoth backup --out ~/backups
Master password:
✓  Backup saved to ~/backups/ciphermoth_backup_20260314_120000.zip

# Import with overwrite
$ ciphermoth import ciphermoth_backup_20260314_120000.zip --on-conflict overwrite
Master password:
✓  Import complete - 3 added, 1 overwritten, 0 skipped
```
