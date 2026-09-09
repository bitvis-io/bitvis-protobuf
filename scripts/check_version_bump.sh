#!/bin/sh
# Require pyproject.toml to change whenever src/ changes.

set -e

if [ -n "${PRE_COMMIT_FROM_REF:-}" ] && [ -n "${PRE_COMMIT_TO_REF:-}" ]; then
  changed=$(git diff --name-only "$PRE_COMMIT_FROM_REF" "$PRE_COMMIT_TO_REF")
else
  changed=$(git diff --cached --name-only HEAD)
fi

if printf '%s\n' "$changed" | grep -qx pyproject.toml; then
  exit 0
fi

echo "src/ changed but pyproject.toml was not updated." >&2
echo "Bump the version in pyproject.toml in the same commit." >&2
exit 1
