#!/usr/bin/env bash

set -euo pipefail

echo 'Running DB migrations...'
alembic upgrade head
echo 'DB migrations completed!'
