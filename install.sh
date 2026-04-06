#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_ROOT="${1:-${HOME}/.claude}"

mkdir -p "${TARGET_ROOT}/skills" "${TARGET_ROOT}/commands"
rm -rf "${TARGET_ROOT}/skills/image-audit"
cp -R "${ROOT_DIR}/.claude/skills/image-audit" "${TARGET_ROOT}/skills/"
cp "${ROOT_DIR}/.claude/commands/imageaudit.md" "${TARGET_ROOT}/commands/imageaudit.md"

echo "Installed image-audit to ${TARGET_ROOT}/skills/image-audit"
echo "Run /imageaudit inside a repo. Use /imageaudit fix to apply safe conversions."
