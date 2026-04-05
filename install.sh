#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-${HOME}/.claude/skills}"

mkdir -p "${TARGET_DIR}"
rm -rf "${TARGET_DIR}/image-audit"
cp -R "${ROOT_DIR}/.claude/skills/image-audit" "${TARGET_DIR}/"

echo "Installed image-audit to ${TARGET_DIR}"
