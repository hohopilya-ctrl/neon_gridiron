#!/usr/bin/env bash
set -euo pipefail

branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$branch" != "main" ]]; then
  echo "ERROR: current branch is '$branch'. Switch to 'main' first."
  exit 1
fi

echo "OK: branch is main"
