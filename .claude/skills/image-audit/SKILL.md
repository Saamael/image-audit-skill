---
description: Audit repo or storage images for wasteful formats, oversized assets, duplicate binaries, and safe WebP conversion opportunities. Use when someone wants a safe image audit, low-risk repo optimizations, or a plan to replace bloated PNG and JPG assets without blindly converting everything.
allowed-tools: Bash Read Grep Glob Edit Write
---

# Image Audit

Interpret `$ARGUMENTS` as one of these modes:

- `audit [path]`
- `fix [path]`
- `supabase-audit <bucket>[,<bucket>...]`

If `$ARGUMENTS` is empty, default to `audit .`.

## Rules

1. Default to read-only unless the user explicitly asks to fix or apply changes.
2. Audit before mutate.
3. Do not assume every PNG wants lossy WebP.
4. Prefer SVG for logos, icons, and simple graphics when possible.
5. Keep originals unless the user explicitly asks to delete or replace them.
6. Only keep converted outputs when they are actually smaller and visually safe.
7. Only update references when the replacement is exact and safe to verify.
8. For Supabase, separate delivery transforms from real storage migration work.

## Backend discovery

Before converting anything, inspect the repo and machine for available tooling.
Prefer this order:

1. repo-native tooling already present in the project, such as `sharp`
2. `cwebp`
3. `magick`
4. `python` with Pillow available
5. `ffmpeg`

If none exist, stop after the audit and explain which backend is missing.
For Python, verify Pillow first instead of assuming it is installed.

## Audit workflow

1. Resolve the target path. If none is given, use the current repo root.
2. Inventory image files and likely references. Prefer fast search tools such as `rg --files` and `rg -n` when available.
3. Call out:
   - biggest raster assets
   - duplicate binaries
   - likely hero or LCP images
   - assets much larger than their likely display size
   - direct PNG and JPG to WebP opportunities
   - files that probably want SVG or lossless handling
4. Group findings into:
   - safe now
   - manual review
   - keep as-is
5. Write a concise report to `reports/image-audit.md`.
6. End with the next command to run.

## Classification

Safe now:

- most JPG and JPEG files
- large opaque PNG photos, covers, banners, hero images, and backgrounds

Manual review:

- logos, icons, favicons, badges, marks, and simple diagrams
- screenshots, dashboards, UI captures, and code images
- alpha-heavy PNG assets
- animated GIFs
- ambiguous or very small PNGs

Keep as-is:

- SVG assets
- files already on WebP or AVIF unless they are obviously oversized

## Fix workflow

When mode is `fix`:

1. Run the audit first and create or update `reports/image-audit.md`.
2. Choose the best available backend.
3. Convert only the safe-now set.
4. Write converted files next to the originals as `.webp`.
5. Compare source vs output size and discard outputs that are larger or only a negligible win.
6. If references are explicit literal file paths and the replacement is one-to-one, update them.
7. If references are dynamic, ambiguous, or framework-controlled, leave them alone and call them out.
8. Write a concise mutation report to `reports/image-fix.md`.

## Supabase workflow

If the user asks for storage audit:

- inspect bucket objects and classify likely migration candidates
- distinguish quick delivery wins from real object migration work
- do not claim the bucket is cleaned up just because transformed URLs exist

## What to report

Always mention:

- what was audited
- which backend was detected
- safe wins
- manual review items
- what was changed, if anything
- estimated bytes saved
- whether references were updated or left alone
