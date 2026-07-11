#!/usr/bin/env bash
set -uo pipefail

CONTROL_DIR="${UPDATE_CONTROL_DIR:-/update-control}"
COMPOSE_FILE="${COMPOSE_FILE:-/work/docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-/work/.env}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"

IMAGE_REPO="${IMAGE_REPO:-ghcr.io/mr-grj/ciphermoth}"
SERVICES="${SERVICES:-backend frontend}"

COSIGN_IDENTITY_REGEXP="${COSIGN_IDENTITY_REGEXP:-^https://github.com/mr-grj/ciphermoth/\.github/workflows/release\.yml@refs/tags/v.*}"
COSIGN_OIDC_ISSUER="${COSIGN_OIDC_ISSUER:-https://token.actions.githubusercontent.com}"

HEALTH_URL="${HEALTH_URL:-http://backend:80/api/meta}"
HEALTH_RETRIES="${HEALTH_RETRIES:-60}"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-3}"
POLL_INTERVAL="${POLL_INTERVAL:-5}"

REQUEST_FILE="${CONTROL_DIR}/request.json"
RESULT_FILE="${CONTROL_DIR}/result.json"
READY_FILE="${CONTROL_DIR}/updater.ready"

log() { echo "[updater] $*" >&2; }

compose() { docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"; }

write_result() {
  local tmp
  tmp="$(mktemp "${CONTROL_DIR}/result.XXXXXX")"
  jq -n \
    --arg state "$1" --arg detail "$2" --arg target "${3:-}" \
    --arg finished_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{state:$state, detail:$detail, target:$target, finished_at:$finished_at}' \
    >"$tmp" && mv "$tmp" "$RESULT_FILE"
}

current_version() {
  local v
  v="$(grep -E '^CIPHERMOTH_VERSION=' "$ENV_FILE" 2>/dev/null | head -n1 | cut -d= -f2-)"
  echo "${v:-latest}"
}

set_version() {
  if grep -qE '^CIPHERMOTH_VERSION=' "$ENV_FILE" 2>/dev/null; then
    sed -i "s|^CIPHERMOTH_VERSION=.*|CIPHERMOTH_VERSION=$1|" "$ENV_FILE"
  else
    echo "CIPHERMOTH_VERSION=$1" >>"$ENV_FILE"
  fi
}

verify_images() {
  local target="$1" svc ref digest
  for svc in $SERVICES; do
    ref="${IMAGE_REPO}-${svc}:${target}"
    log "pulling ${ref}"
    if ! docker pull "$ref" >&2; then
      log "pull failed for ${ref}"
      return 1
    fi
    digest="$(docker inspect --format '{{index .RepoDigests 0}}' "$ref" 2>/dev/null)"
    if [ -z "$digest" ]; then
      log "could not resolve digest for ${ref}"
      return 1
    fi
    log "verifying signature of ${digest}"
    if ! cosign verify \
      --certificate-identity-regexp "$COSIGN_IDENTITY_REGEXP" \
      --certificate-oidc-issuer "$COSIGN_OIDC_ISSUER" \
      "$digest" >&2; then
      log "SIGNATURE VERIFICATION FAILED for ${digest}"
      return 1
    fi
  done
  return 0
}

snapshot_db() {
  mkdir -p "$BACKUP_DIR"
  local out="${BACKUP_DIR}/ciphermoth-$(date -u +%Y%m%dT%H%M%SZ).sql"
  log "snapshotting database to ${out}"
  if PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
    -h "${POSTGRES_HOST:-db}" -U "${POSTGRES_USER:-ciphermoth}" \
    -d "${POSTGRES_DB:-ciphermoth}" -f "$out"; then
    log "snapshot ok"
  else
    log "WARNING: database snapshot failed; continuing"
  fi
}

health_ok() {
  local target="$1" i got
  for i in $(seq 1 "$HEALTH_RETRIES"); do
    got="$(curl -fsS "$HEALTH_URL" 2>/dev/null | jq -r '.version' 2>/dev/null)"
    if [ "v${got#v}" = "v${target#v}" ]; then
      return 0
    fi
    sleep "$HEALTH_INTERVAL"
  done
  return 1
}

process_request() {
  local target prev
  target="$(jq -r '.target // empty' "$REQUEST_FILE" 2>/dev/null)"
  rm -f "$REQUEST_FILE"
  if [ -z "$target" ]; then
    log "empty/invalid request; ignoring"
    return
  fi
  prev="$(current_version)"
  log "update requested: ${prev} -> ${target}"

  write_result "verifying" "Verifying image signatures" "$target"
  if ! verify_images "$target"; then
    write_result "failed" "Image signature verification failed. Nothing was changed." "$target"
    return
  fi

  snapshot_db

  write_result "applying" "Applying update and restarting" "$target"
  set_version "$target"
  if ! compose up -d $SERVICES >&2; then
    log "compose up failed; rolling back"
    set_version "$prev"
    compose up -d $SERVICES >&2 || true
    write_result "rolled_back" "Restart failed; rolled back to ${prev}." "$prev"
    return
  fi

  if health_ok "$target"; then
    write_result "success" "Updated to ${target}." "$target"
    log "update to ${target} succeeded"
  else
    log "health check failed; rolling back to ${prev}"
    set_version "$prev"
    compose up -d $SERVICES >&2 || true
    write_result "rolled_back" "New version failed its health check; rolled back to ${prev}." "$prev"
  fi
}

main() {
  mkdir -p "$CONTROL_DIR"
  : >"$READY_FILE"
  log "ready; watching ${REQUEST_FILE}"
  while true; do
    if [ -f "$REQUEST_FILE" ]; then
      process_request
    fi
    sleep "$POLL_INTERVAL"
  done
}

main
