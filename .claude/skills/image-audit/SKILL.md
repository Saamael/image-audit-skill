---
description: Audit a repo or Supabase bucket for oversized or wrong-format images, then build a safe WebP migration plan. Use when someone wants to find PNG and JPG bloat, duplicate assets, lazy-loading issues, or storage cleanup work.
allowed-tools: Bash Read Grep Glob Edit Write
---

# Image Audit

Interpret `$ARGUMENTS` as one of these modes:

- `audit <path>`
- `plan <path>`
- `apply <plan-file>`
- `supabase-audit <bucket>[,<bucket>...]`

If `$ARGUMENTS` is empty, default to `audit .`.

## Find the helper script first

Prefer the first existing path:

- `./.claude/skills/image-audit/scripts/image_audit.py`
- `~/.claude/skills/image-audit/scripts/image_audit.py`

Use that script path in every command below.

## Rules

1. Audit before mutate.
2. Do not assume every PNG should become lossy WebP.
3. Treat Supabase delivery transforms and storage migration as different jobs.
4. Keep originals unless the user explicitly asks to delete them.
5. End every run with safe changes, manual review items, and the next command to run.

## Local repo workflow

### Audit

Run:

```bash
python "<script-path>" audit --root "<path>" --json-output reports/image-audit.json --markdown-output reports/image-audit.md
```

Then summarize:

- biggest files
- duplicate assets
- likely hero or LCP risks
- safe WebP candidates
- files that need manual review because they may want SVG or lossless handling

### Plan

Run:

```bash
python "<script-path>" plan --root "<path>" --json-output reports/image-plan.json --markdown-output reports/image-plan.md
```

Group the plan into:

- safe to convert now
- manual review
- keep as-is

### Apply

Run:

```bash
python "<script-path>" apply --plan "<plan-file>"
```

Important:

- this only converts safe local files
- it keeps originals in place
- it does not pretend code references are fixed unless you verify them

## Supabase workflow

If the user wants a storage audit, run:

```bash
python "<script-path>" supabase-audit --bucket "<bucket>" --json-output reports/supabase-audit.json --markdown-output reports/supabase-audit.md
```

The script reads:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

unless the user passes explicit flags.

For Supabase, distinguish:

- quick delivery wins
- actual storage migration work

Do not imply the bucket is cleaned up just because transformed delivery URLs exist.

## What to call out

Always mention if you find:

- giant PNGs that should probably be WebP
- JPGs that are easy WebP wins
- screenshots, logos, or alpha-heavy assets that need manual review
- duplicate binaries
- large hero images
- assets much larger than their likely display size
- places where SVG or CSS would beat raster files
