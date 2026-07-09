#!/bin/sh
set -e

API_URL="${VITE_API_URL:-http://localhost:8000/api}"

if grep -rq "__DINOPASS_API_URL__" /app/dist 2>/dev/null; then
  echo "Setting API URL to ${API_URL}"
  find /app/dist -type f -name '*.js' \
    -exec sed -i "s|__DINOPASS_API_URL__|${API_URL}|g" {} \;
fi

exec serve -s dist -l 3000 -c /app/serve.json
