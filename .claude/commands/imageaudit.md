---
description: Audit and safely optimize images in the current repo
argument-hint: [optional path or extra instruction]
allowed-tools: Bash(python:*), Read, Grep, Glob, Edit, Write
---

Use the installed `image-audit` skill and do as much safe image optimization work as you can for the current repo.

Default behavior:

1. Treat `$ARGUMENTS` as an optional target path or extra instruction.
2. If no path is given, use the current working directory.
3. Find the helper script at one of:
   - `./.claude/skills/image-audit/scripts/image_audit.py`
   - `~/.claude/skills/image-audit/scripts/image_audit.py`
4. Run a local audit and plan:
   - `python "<script-path>" audit --root "<target-path>" --json-output reports/image-audit.json --markdown-output reports/image-audit.md`
   - `python "<script-path>" plan --root "<target-path>" --json-output reports/image-plan.json --markdown-output reports/image-plan.md`
5. Unless the user explicitly says `audit only`, `report only`, `plan only`, or `dry run`, apply the safe local conversions:
   - `python "<script-path>" apply --plan reports/image-plan.json --json-output reports/image-apply.json --markdown-output reports/image-apply.md`
6. Never delete originals.
7. Summarize:
   - what was audited
   - what was safely converted
   - approximate bytes saved
   - what still needs manual review
   - whether code refs may still need cleanup

If `$ARGUMENTS` mentions Supabase or bucket names, also run a Supabase audit when the required env vars are present.
