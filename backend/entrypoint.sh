#!/usr/bin/env bash
set -euo pipefail
alembic upgrade head
exec uvicorn main:app --workers 1 --host 0.0.0.0 --port 80
