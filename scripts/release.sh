#!/usr/bin/env bash
# Cut a CipherMoth release: bump versions, stamp the changelog, commit, tag,
# push, and publish a GitHub release. Pushing the tag triggers the image-publish
# workflow (which signs the images); the GitHub *release* is what the in-app
# update check reads via /releases/latest.
#
#   scripts/release.sh 1.1.0            # do it
#   scripts/release.sh 1.1.0 --dry-run  # show what would change, touch nothing
#
# Idempotent on the bumps: files already at the target version are left as-is,
# so it's safe to run after a manual bump.
set -euo pipefail

VERSION="${1:-}"
DRY_RUN="${2:-}"

die() {
  printf '\033[31m✗ %s\033[0m\n' "$*" >&2
  exit 1
}
say() { printf '\033[38;5;79m▪\033[0m %s\n' "$*"; }

VERSION="${VERSION#v}"
[ -n "$VERSION" ] || die "usage: scripts/release.sh <X.Y.Z> [--dry-run]"
echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$' || die "version must be X.Y.Z (got '$VERSION')"
TAG="v${VERSION}"
DATE="$(date -u +%Y-%m-%d)"

cd "$(git rev-parse --show-toplevel)"

command -v gh >/dev/null 2>&1 || die "the GitHub CLI (gh) is required: https://cli.github.com"
gh auth status >/dev/null 2>&1 || die "not logged in to gh - run: gh auth login"
command -v uv >/dev/null 2>&1 || die "uv is required (backend lockfile)"

branch="$(git rev-parse --abbrev-ref HEAD)"
[ "$branch" = "master" ] || die "releases are cut from master (you're on '$branch')"
git rev-parse "$TAG" >/dev/null 2>&1 && die "tag $TAG already exists"

cur_be="$(sed -nE 's/^version = "(.*)"/\1/p' backend/pyproject.toml | head -1)"
cur_fe="$(sed -nE 's/.*"version": "([^"]*)".*/\1/p' frontend/package.json | head -1)"

say "Releasing ${TAG} (backend ${cur_be} → ${VERSION}, frontend ${cur_fe} → ${VERSION})"

if [ "$cur_be" != "$VERSION" ]; then
  sed -i.bak -E "s/^version = \".*\"/version = \"${VERSION}\"/" backend/pyproject.toml
  rm -f backend/pyproject.toml.bak
  say "Bumped backend/pyproject.toml"
  (cd backend && uv lock >/dev/null)
  say "Relocked backend/uv.lock"
fi

if [ "$cur_fe" != "$VERSION" ]; then
  (cd frontend && npm --no-git-tag-version version "$VERSION" >/dev/null)
  say "Bumped frontend/package.json"
fi

if ! grep -qE "^## \[${VERSION//./\\.}\]" CHANGELOG.md; then
  awk -v ver="$VERSION" -v date="$DATE" '
    !done && /^## \[Unreleased\]/ {
      print "## [Unreleased]"; print ""; print "## [" ver "] - " date;
      done=1; next
    }
    { print }
  ' CHANGELOG.md >CHANGELOG.tmp && mv CHANGELOG.tmp CHANGELOG.md
  say "Stamped CHANGELOG.md"
fi

notes="$(mktemp)"
awk -v ver="$VERSION" '
  $0 ~ "^## \\[" ver "\\]" { insec=1; next }
  insec && /^## \[/ { exit }
  insec { print }
' CHANGELOG.md | sed '/./,$!d' >"$notes"
[ -s "$notes" ] || printf 'Release %s\n' "$TAG" >"$notes"

files="backend/pyproject.toml backend/uv.lock frontend/package.json frontend/package-lock.json CHANGELOG.md"

if [ "$DRY_RUN" = "--dry-run" ]; then
  say "DRY RUN - changes that would be committed:"
  # shellcheck disable=SC2086
  git --no-pager diff -- $files || true
  printf '\n'
  say "Release notes that would be published:"
  cat "$notes"
  # shellcheck disable=SC2086
  git checkout -- $files 2>/dev/null || true
  rm -f "$notes"
  say "Reverted. Nothing was committed, tagged, or pushed."
  exit 0
fi

# shellcheck disable=SC2086
git add $files
git commit -m "chore: release ${TAG}"
git tag -a "$TAG" -m "$TAG"
say "Committed and tagged ${TAG}"

git push origin "$branch"
git push origin "$TAG"
say "Pushed - the image-publish workflow is now building & signing images"

gh release create "$TAG" --title "$TAG" --notes-file "$notes"
rm -f "$notes"
say "Published GitHub release ${TAG}. Done."
