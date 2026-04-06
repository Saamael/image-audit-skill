# Image Audit

Audit repo images and apply only the safe fixes.

Repo: https://github.com/Saamael/image-audit-skill

## Install

Claude Code:

```bash
npx image-audit-skill install --claude
```

Then inside a repo, run:

```bash
/imageaudit
```

Apply safe fixes explicitly:

```bash
/imageaudit fix
```

Codex:

```bash
npx image-audit-skill install --codex
```

Then ask Codex:

- `Use the image-audit skill to audit this repo.`
- `Use the image-audit skill to apply safe image fixes in this repo.`

## What it does

- audits repo images, references, duplicates, and oversized assets
- classifies safe WebP wins vs manual-review files
- uses the best image tool already available on the machine
- keeps originals
- updates references only when the replacement is exact and safe

## Safe by default

- `/imageaudit` is audit-only
- `/imageaudit fix` is explicit apply mode
- logos, icons, screenshots, alpha-heavy PNGs, and SVG candidates are not blindly converted

## Backends it can use

In order:

- repo-native tooling like `sharp`
- `cwebp`
- `magick`
- `python` with Pillow
- `ffmpeg`

If none are available, it still audits the repo and tells you what is missing.

This package does not ship a bundled optimizer script. The agent uses what the repo or machine already has.

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

## Claude Code usage

```bash
/imageaudit
```

```bash
/imageaudit src
```

```bash
/imageaudit fix
```

```bash
/imageaudit fix src
```

```bash
/imageaudit supabase blog-images
```

Supabase audits expect:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## Codex usage

After install, ask Codex to use the skill directly:

- `Use the image-audit skill to audit this repo and tell me what is safe to optimize.`
- `Use the image-audit skill to apply safe image fixes in this repo.`

## Summary

- Install:

```bash
npx image-audit-skill install --claude
```

- Run:

```bash
/imageaudit
```

- Fix:

```bash
/imageaudit fix
```
