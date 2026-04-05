# Image Audit

Safely optimize images in your repo.

Repo: https://github.com/Saamael/image-audit-skill

## Recommended install

Claude Code:

```bash
npx image-audit-skill install --claude
```

Then inside a repo, run:

```bash
/imageaudit
```

That is the main happy path.

## What it does

- audits local image assets and image references
- builds a safe plan
- applies safe local conversions when possible
- leaves risky files for manual review
- can audit Supabase Storage too

## What it does not do

- blindly convert every PNG
- delete originals
- pretend screenshots, logos, and alpha-heavy assets all want the same treatment

## Requirements

- Python 3.10+
- Pillow
- Node 18+

Install Pillow if needed:

```bash
pip install Pillow
```

## Other install options

Claude Code, current project only:

```bash
npx image-audit-skill install --claude --project .
```

Codex:

```bash
npx image-audit-skill install --codex
```

Codex, current project only:

```bash
npx image-audit-skill install --codex --project .
```

## Usage

In Claude Code:

```bash
/imageaudit
```

You can also pass extra instructions:

```bash
/imageaudit audit only
```

```bash
/imageaudit src
```

```bash
/imageaudit check supabase bucket blog-images too
```

Without the command, you can still ask:

- `Audit this repo for image bloat and tell me what is safe to convert.`
- `Plan a PNG to WebP migration for this project without breaking refs.`

## Direct script usage

The helper script lives in:

```bash
./.claude/skills/image-audit/scripts/image_audit.py
```

Local audit:

```bash
python ./.claude/skills/image-audit/scripts/image_audit.py audit --root . --json-output reports/image-audit.json --markdown-output reports/image-audit.md
```

Local plan:

```bash
python ./.claude/skills/image-audit/scripts/image_audit.py plan --root . --json-output reports/image-plan.json --markdown-output reports/image-plan.md
```

Apply safe local conversions:

```bash
python ./.claude/skills/image-audit/scripts/image_audit.py apply --plan reports/image-plan.json
```

Supabase bucket audit:

```bash
python ./.claude/skills/image-audit/scripts/image_audit.py supabase-audit --bucket blog-images --json-output reports/supabase-audit.json --markdown-output reports/supabase-audit.md
```

## Summary

- Install:

```bash
npx image-audit-skill install --claude
```

- Run:

```bash
/imageaudit
```

- It will do as much safe optimization as it can.

npm:

```bash
npm login
npm publish --access public
```
