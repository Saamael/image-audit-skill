---
description: Audit repo images and run safe fixes when explicitly asked
argument-hint: [path | fix [path] | supabase <bucket>]
allowed-tools: Bash, Read, Grep, Glob, Edit, Write
---

Use the installed `image-audit` skill.

Interpret `$ARGUMENTS` like this:

- empty -> `audit .`
- `<path>` -> `audit <path>`
- `fix` or `fix <path>` -> audit first, then apply safe local fixes
- `supabase <bucket>[,<bucket>...]` -> audit Supabase storage only

Command contract:

1. `/imageaudit` without `fix` is read-only.
2. Always create or update `reports/image-audit.md`.
3. In `fix` mode, also create `reports/image-fix.md`.
4. Detect available local tooling and use the best installed backend.
5. Keep originals.
6. Only keep converted outputs if they are actually smaller.
7. Only update references when the replacement is exact and safe.
8. If no conversion backend exists, finish with the audit and explain what to install next.

Default summary:

- what was audited
- which backend was detected
- safe wins
- manual review items
- what was changed, if anything
- next command to run
