# Image Audit

Audit-first image cleanup for Claude Code and Codex.

Repo: https://github.com/Saamael/image-audit-skill

This is built for a boring but common problem:

- solo founders upload PNGs by default
- sites accumulate oversized assets
- nobody knows which files are safe WebP wins and which ones need manual review

The skill is audit-first.
It scans first, plans second, and only applies safe local conversions when asked.

## What it does

- audits local image assets and code references
- flags duplicate files by hash
- highlights likely hero and LCP assets
- classifies PNG and JPG files into safe conversions vs manual review
- generates JSON and Markdown reports
- builds a local migration plan
- converts safe local files to WebP while keeping originals
- audits Supabase Storage buckets for remote migration candidates

## What it does not do yet

- rewrite every code reference automatically
- migrate Supabase objects in place
- decide every PNG should become lossy WebP

## Requirements

- Python 3.10+
- Pillow
- Node 18+ if you want the `npx` installer

Install Pillow if needed:

```bash
pip install Pillow
```

## Recommended install

If you publish this repo to npm, the cleanest install flow is:

Claude Code global:

```bash
npx image-audit-skill install --claude
```

Claude Code project-local:

```bash
npx image-audit-skill install --claude --project .
```

Codex global:

```bash
npx image-audit-skill install --codex
```

Codex project-local:

```bash
npx image-audit-skill install --codex --project .
```

This is nicer than raw copy commands because the package just drops the skill into the right folder.

## Repo and package

- GitHub repo: `Saamael/image-audit-skill`
- npm package: `image-audit-skill`
- Skill folder: `image-audit`

## Install globally

Quickest option:

macOS or Linux:

```bash
./install.sh
```

Windows PowerShell:

```powershell
.\install.ps1
```

Manual install:

macOS or Linux:

```bash
mkdir -p ~/.claude/skills
cp -R ./.claude/skills/image-audit ~/.claude/skills/
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\\.claude\\skills" | Out-Null
Copy-Item -Recurse ".\\.claude\\skills\\image-audit" "$HOME\\.claude\\skills\\"
```

## Install per project

macOS or Linux:

```bash
./install.sh /path/to/target-project/.claude/skills
```

Windows PowerShell:

```powershell
.\install.ps1 "C:\path\to\target-project\.claude\skills"
```

## Install scripts

The helper script lives inside the skill folder.
Once installed, Claude Code can find it in one of these locations:

- `./.claude/skills/image-audit/scripts/image_audit.py`
- `~/.claude/skills/image-audit/scripts/image_audit.py`

## Usage

After install, ask Claude Code things like:

- `Audit this repo for image bloat and tell me what is safe to convert.`
- `Plan a PNG to WebP migration for this project without breaking refs.`
- `Audit these Supabase buckets for oversized images: blog-images, blog-covers.`

## Direct script usage

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
SUPABASE_URL="https://your-project.supabase.co" \
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key" \
python ./.claude/skills/image-audit/scripts/image_audit.py supabase-audit \
  --bucket blog-images \
  --bucket blog-covers \
  --json-output reports/supabase-audit.json \
  --markdown-output reports/supabase-audit.md
```

## Sharing

The simplest first release is a GitHub repo with this exact folder structure.

Then the install story is:

1. Push the repo to GitHub: `https://github.com/Saamael/image-audit-skill`
2. Publish the npm package: `image-audit-skill`
3. Tell Claude Code users to run `npx image-audit-skill install --claude`.
4. Tell Codex users to run `npx image-audit-skill install --codex`.

## GitHub fallback

macOS or Linux:

```bash
git clone https://github.com/Saamael/image-audit-skill.git
cd image-audit-skill
./install.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/Saamael/image-audit-skill.git
cd image-audit-skill
.\install.ps1
```

## Publish

GitHub:

```bash
git add .
git commit -m "Prepare first public release"
git push origin main
```

npm:

```bash
npm login
npm publish --access public
```
