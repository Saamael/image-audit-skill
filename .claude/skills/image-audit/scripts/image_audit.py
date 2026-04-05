from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".svg", ".gif", ".bmp", ".tif", ".tiff"}
TEXT_EXTS = {
    ".js", ".jsx", ".ts", ".tsx", ".json", ".html", ".css", ".scss", ".md", ".mdx", ".txt",
    ".astro", ".vue", ".svelte", ".xml", ".yml", ".yaml", ".toml", ".sql", ".py", ".php",
}
SKIP_DIRS = {
    ".git", ".next", ".nuxt", ".svelte-kit", ".vercel", ".cache", ".idea", ".vscode", ".turbo",
    "node_modules", "dist", "build", "out", "coverage", "vendor", "__pycache__",
}
VECTOR_HINTS = {"logo", "icon", "favicon", "wordmark", "badge", "sprite", "mark"}
SCREEN_HINTS = {"screenshot", "screen", "ui", "dashboard", "mockup", "diagram", "wireframe", "chart", "graph", "code"}
PHOTO_HINTS = {"photo", "hero", "cover", "banner", "background", "thumbnail", "avatar", "gallery", "team", "product", "header"}
LCP_HINTS = {"hero", "cover", "banner", "landing", "og", "social", "header"}
REF_RE = re.compile(r"(?P<ref>[^\"'\s<>()]+?\.(?:png|jpe?g|gif|svg|webp|avif))(?:[?#][^\"'\s<>()]*)?", re.I)


def require_pillow() -> None:
    if Image is None:
        raise SystemExit("Pillow is required. Install it with: pip install Pillow")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: str | None, data: dict) -> None:
    payload = json.dumps(data, indent=2)
    if path:
        output = Path(path)
        ensure_parent(output)
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


def write_md(path: str | None, text: str) -> None:
    if not path:
        return
    output = Path(path)
    ensure_parent(output)
    output.write_text(text, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path) -> list[Path]:
    files = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS and not name.startswith(".venv")]
        base = Path(current_root)
        for name in filenames:
            files.append(base / name)
    return files


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def read_image_meta(path: Path) -> dict:
    meta = {"width": None, "height": None, "mode": None, "has_alpha": None}
    if path.suffix.lower() == ".svg":
        return meta
    require_pillow()
    with Image.open(path) as image:
        meta["width"], meta["height"] = image.size
        meta["mode"] = image.mode
        meta["has_alpha"] = "A" in image.getbands() or image.mode in {"RGBA", "LA"}
    return meta


def usage_hint(path_text: str) -> str:
    lowered = path_text.lower()
    if any(token in lowered for token in VECTOR_HINTS):
        return "logo-or-icon"
    if any(token in lowered for token in SCREEN_HINTS):
        return "ui-or-screenshot"
    if any(token in lowered for token in PHOTO_HINTS):
        return "photo-or-hero"
    if "og" in lowered or "social" in lowered:
        return "social-card"
    return "generic"


def resolve_ref(root: Path, source_file: Path, raw_ref: str) -> str | None:
    ref = raw_ref.split("?", 1)[0].split("#", 1)[0].replace("\\", "/")
    if "://" in ref or ref.startswith("data:") or ref.startswith("@") or ref.startswith("~"):
        return None
    candidate = root / ref.lstrip("/") if ref.startswith("/") else (source_file.parent / ref).resolve(strict=False)
    try:
        return candidate.relative_to(root).as_posix()
    except ValueError:
        return None


def scan_references(root: Path, files: list[Path]) -> tuple[dict, dict]:
    exact = defaultdict(set)
    fallback = defaultdict(set)
    for file_path in files:
        ext = file_path.suffix.lower()
        if ext not in TEXT_EXTS and not (ext == "" and file_path.stat().st_size < 262144):
            continue
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        source_rel = rel(root, file_path)
        for match in REF_RE.finditer(text):
            raw = match.group("ref")
            fallback[Path(raw).name].add(source_rel)
            resolved = resolve_ref(root, file_path, raw)
            if resolved:
                exact[resolved].add(source_rel)
    return exact, fallback


def classify_local(item: dict) -> dict:
    extension = item["extension"]
    size_bytes = item["size_bytes"]
    width = item["width"] or 0
    height = item["height"] or 0
    usage = item["usage"]
    has_alpha = bool(item["has_alpha"])
    reasons = []

    if extension == ".svg":
        return {"action": "keep", "target_format": "svg", "safe_to_apply": False, "manual_review": False, "reasons": ["Vector assets should usually stay vector."]}
    if extension == ".gif":
        return {"action": "manual-review", "target_format": "gif", "safe_to_apply": False, "manual_review": True, "reasons": ["GIFs usually need manual handling."]}
    if extension in {".webp", ".avif"}:
        reasons.append("Already on a modern delivery format.")
        if size_bytes > 600000 or width > 2400 or height > 2400:
            reasons.append("Still large enough to review.")
            return {"action": "manual-review", "target_format": extension.lstrip("."), "safe_to_apply": False, "manual_review": True, "reasons": reasons}
        return {"action": "keep", "target_format": extension.lstrip("."), "safe_to_apply": False, "manual_review": False, "reasons": reasons}

    if usage == "logo-or-icon":
        return {"action": "manual-review", "target_format": "svg-or-lossless-webp", "safe_to_apply": False, "manual_review": True, "reasons": ["Logos and icons often want SVG or lossless handling."]}
    if usage == "ui-or-screenshot":
        return {"action": "manual-review", "target_format": "lossless-webp", "safe_to_apply": False, "manual_review": True, "reasons": ["Screenshots and UI assets should not be converted blindly."]}

    if extension in {".jpg", ".jpeg"}:
        reasons.append("JPEG files are usually safe WebP wins.")
        if any(token in item["path"] for token in LCP_HINTS):
            reasons.append("Looks like a likely hero or LCP asset.")
        return {"action": "convert-to-webp", "target_format": "webp", "safe_to_apply": True, "manual_review": False, "reasons": reasons}

    if extension == ".png":
        if not has_alpha and (size_bytes >= 180000 or usage == "photo-or-hero" or width >= 1600):
            reasons.append("PNG looks like a safe lossy WebP candidate.")
            if any(token in item["path"] for token in LCP_HINTS):
                reasons.append("Looks like a likely hero or LCP asset.")
            return {"action": "convert-to-webp", "target_format": "webp", "safe_to_apply": True, "manual_review": False, "reasons": reasons}
        if has_alpha and size_bytes >= 220000:
            return {"action": "manual-review", "target_format": "lossless-webp", "safe_to_apply": False, "manual_review": True, "reasons": ["Alpha-heavy PNG should be reviewed before conversion."]}
        return {"action": "manual-review", "target_format": "webp", "safe_to_apply": False, "manual_review": True, "reasons": ["PNG is small or ambiguous enough to review manually."]}

    return {"action": "manual-review", "target_format": extension.lstrip("."), "safe_to_apply": False, "manual_review": True, "reasons": ["Unknown image type."]}


def local_audit(root: Path) -> dict:
    files = iter_files(root)
    images = [path for path in files if path.suffix.lower() in IMAGE_EXTS]
    exact_refs, fallback_refs = scan_references(root, files)
    hashes = defaultdict(list)
    rows = []

    for image_path in images:
        path_text = rel(root, image_path)
        meta = read_image_meta(image_path)
        exact_files = sorted(exact_refs.get(path_text, set()))
        basename_files = sorted(fallback_refs.get(image_path.name, set()))
        refs = exact_files if exact_files else basename_files
        row = {
            "path": path_text,
            "name": image_path.name,
            "extension": image_path.suffix.lower(),
            "size_bytes": image_path.stat().st_size,
            "width": meta["width"],
            "height": meta["height"],
            "mode": meta["mode"],
            "has_alpha": meta["has_alpha"],
            "usage": usage_hint(path_text),
            "reference_count": len(refs),
            "reference_mode": "exact" if exact_files else ("basename" if basename_files else "unreferenced"),
            "reference_files": refs,
            "sha256": sha256(image_path),
        }
        row["recommendation"] = classify_local(row)
        rows.append(row)
        hashes[row["sha256"]].append(path_text)

    for row in rows:
        row["duplicate_paths"] = [path for path in hashes[row["sha256"]] if path != row["path"]]

    rows.sort(key=lambda item: item["size_bytes"], reverse=True)
    return {
        "mode": "audit",
        "root": str(root),
        "summary": {
            "image_count": len(rows),
            "total_bytes": sum(item["size_bytes"] for item in rows),
            "safe_convert_count": sum(1 for item in rows if item["recommendation"]["safe_to_apply"]),
            "manual_review_count": sum(1 for item in rows if item["recommendation"]["manual_review"]),
            "unreferenced_count": sum(1 for item in rows if item["reference_count"] == 0),
            "duplicate_groups": sum(1 for group in hashes.values() if len(group) > 1),
        },
        "images": rows,
    }


def local_plan(audit: dict) -> dict:
    items = []
    for image in audit["images"]:
        rec = image["recommendation"]
        items.append({
            "path": image["path"],
            "current_format": image["extension"].lstrip("."),
            "proposed_path": Path(image["path"]).with_suffix(".webp").as_posix() if rec["target_format"] in {"webp", "lossless-webp"} else None,
            "action": rec["action"],
            "target_format": rec["target_format"],
            "safe_to_apply": rec["safe_to_apply"],
            "manual_review": rec["manual_review"],
            "quality": 80 if rec["action"] == "convert-to-webp" else None,
            "lossless": rec["target_format"] == "lossless-webp",
            "reference_count": image["reference_count"],
            "reference_mode": image["reference_mode"],
            "reference_files": image["reference_files"],
            "duplicate_paths": image["duplicate_paths"],
            "notes": rec["reasons"],
        })
    return {
        "mode": "plan",
        "root": audit["root"],
        "summary": {
            "item_count": len(items),
            "safe_to_apply": sum(1 for item in items if item["safe_to_apply"]),
            "manual_review": sum(1 for item in items if item["manual_review"]),
            "keep": sum(1 for item in items if item["action"] == "keep"),
        },
        "items": items,
    }


def apply_plan(plan_file: Path, overwrite: bool) -> dict:
    require_pillow()
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    root = Path(plan["root"])
    converted, skipped = [], []
    for item in plan["items"]:
        if not item["safe_to_apply"] or not item["proposed_path"]:
            skipped.append({"path": item["path"], "reason": "Not marked safe to apply."})
            continue
        source_path = root / item["path"]
        target_path = root / item["proposed_path"]
        if target_path.exists() and not overwrite:
            skipped.append({"path": item["path"], "reason": "Target already exists."})
            continue
        ensure_parent(target_path)
        with Image.open(source_path) as image:
            save_source = image if image.mode in {"RGB", "RGBA", "LA"} or item["lossless"] else image.convert("RGB")
            kwargs = {"format": "WEBP", "method": 6}
            if item["lossless"]:
                kwargs["lossless"] = True
            else:
                kwargs["quality"] = item["quality"] or 80
            save_source.save(target_path, **kwargs)
        source_bytes = source_path.stat().st_size
        target_bytes = target_path.stat().st_size
        converted.append({
            "source_path": item["path"],
            "target_path": item["proposed_path"],
            "source_bytes": source_bytes,
            "target_bytes": target_bytes,
            "bytes_saved": source_bytes - target_bytes,
        })
    return {
        "mode": "apply",
        "root": str(root),
        "summary": {
            "converted_count": len(converted),
            "skipped_count": len(skipped),
            "bytes_saved": sum(item["bytes_saved"] for item in converted),
        },
        "converted": converted,
        "skipped": skipped,
    }


def supabase_request(url: str, key: str, path: str, payload: dict) -> list[dict]:
    request = urllib.request.Request(
        f"{url.rstrip('/')}{path}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {key}", "apikey": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise SystemExit(f"Supabase request failed: {exc.code} {body}") from exc


def classify_remote(path_text: str, size_bytes: int | None) -> dict:
    extension = Path(path_text).suffix.lower()
    if extension == ".svg":
        return {"action": "keep", "target_format": "svg", "reasons": ["Vector asset, likely fine as SVG."]}
    if extension == ".gif":
        return {"action": "manual-review", "target_format": "gif", "reasons": ["GIF usually needs manual handling."]}
    if extension in {".webp", ".avif"}:
        return {"action": "keep", "target_format": extension.lstrip("."), "reasons": ["Already on a modern image format."]}
    if extension in {".jpg", ".jpeg"}:
        return {"action": "remote-webp-candidate", "target_format": "webp", "reasons": ["Likely remote WebP migration candidate."]}
    if extension == ".png":
        note = "PNG object should be reviewed for WebP or SVG migration."
        if size_bytes and size_bytes >= 180000:
            note = "Large PNG object should be reviewed for WebP or SVG migration."
        return {"action": "remote-review", "target_format": "webp", "reasons": [note]}
    return {"action": "ignore", "target_format": extension.lstrip("."), "reasons": []}


def list_bucket(url: str, key: str, bucket: str, prefix: str) -> list[dict]:
    objects, stack = [], [prefix]
    while stack:
        current = stack.pop()
        offset = 0
        while True:
            page = supabase_request(
                url,
                key,
                f"/storage/v1/object/list/{urllib.parse.quote(bucket, safe='')}",
                {"prefix": current, "limit": 1000, "offset": offset, "sortBy": {"column": "name", "order": "asc"}},
            )
            for entry in page:
                name = entry.get("name")
                if not name:
                    continue
                metadata = entry.get("metadata") or {}
                is_folder = entry.get("id") is None and not metadata
                full_path = f"{current}/{name}".strip("/") if current else name
                if is_folder:
                    stack.append(full_path)
                    continue
                objects.append({
                    "bucket": bucket,
                    "path": full_path,
                    "extension": Path(name).suffix.lower(),
                    "size_bytes": metadata.get("size"),
                    "mimetype": metadata.get("mimetype"),
                })
            if len(page) < 1000:
                break
            offset += 1000
    return objects


def supabase_audit(url: str, key: str, buckets: list[str], prefix: str) -> dict:
    rows = []
    for bucket in buckets:
        for entry in list_bucket(url, key, bucket, prefix):
            if entry["extension"] not in IMAGE_EXTS:
                continue
            entry["recommendation"] = classify_remote(entry["path"], entry["size_bytes"])
            rows.append(entry)
    rows.sort(key=lambda item: item.get("size_bytes") or 0, reverse=True)
    return {
        "mode": "supabase-audit",
        "supabase_url": url,
        "buckets": buckets,
        "prefix": prefix,
        "summary": {
            "bucket_count": len(buckets),
            "image_count": len(rows),
            "total_bytes": sum(item.get("size_bytes") or 0 for item in rows),
            "remote_candidates": sum(1 for item in rows if item["recommendation"]["action"] in {"remote-webp-candidate", "remote-review"}),
        },
        "objects": rows,
    }


def markdown_report(report: dict) -> str:
    mode = report["mode"]
    if mode == "audit":
        lines = [
            "# Image Audit", "",
            f"- Root: `{report['root']}`",
            f"- Images: {report['summary']['image_count']}",
            f"- Total bytes: {report['summary']['total_bytes']}",
            f"- Safe conversions: {report['summary']['safe_convert_count']}",
            f"- Manual review: {report['summary']['manual_review_count']}",
            "",
            "## Biggest files", "",
        ]
        for item in report["images"][:20]:
            note = "; ".join(item["recommendation"]["reasons"][:2])
            lines.append(f"- `{item['path']}` | {item['size_bytes']} bytes | {item['recommendation']['action']} | {note}")
        return "\n".join(lines) + "\n"
    if mode == "plan":
        lines = [
            "# Image Plan", "",
            f"- Root: `{report['root']}`",
            f"- Safe now: {report['summary']['safe_to_apply']}",
            f"- Manual review: {report['summary']['manual_review']}",
            "",
            "## Safe to apply", "",
        ]
        safe_items = [item for item in report["items"] if item["safe_to_apply"]]
        manual_items = [item for item in report["items"] if item["manual_review"]]
        for item in safe_items[:20]:
            lines.append(f"- `{item['path']}` -> `{item['proposed_path']}` | {item['action']}")
        lines.extend(["", "## Manual review", ""])
        for item in manual_items[:20]:
            reason = item["notes"][0] if item["notes"] else "Needs review."
            lines.append(f"- `{item['path']}` | {item['target_format']} | {reason}")
        return "\n".join(lines) + "\n"
    if mode == "apply":
        lines = [
            "# Image Apply Results", "",
            f"- Root: `{report['root']}`",
            f"- Converted: {report['summary']['converted_count']}",
            f"- Skipped: {report['summary']['skipped_count']}",
            f"- Bytes saved: {report['summary']['bytes_saved']}",
            "",
            "## Converted", "",
        ]
        for item in report["converted"][:20]:
            lines.append(f"- `{item['source_path']}` -> `{item['target_path']}` | saved {item['bytes_saved']} bytes")
        return "\n".join(lines) + "\n"
    lines = [
        "# Supabase Image Audit", "",
        f"- URL: `{report['supabase_url']}`",
        f"- Buckets: {', '.join(report['buckets'])}",
        f"- Images: {report['summary']['image_count']}",
        f"- Remote candidates: {report['summary']['remote_candidates']}",
        "",
        "## Biggest objects", "",
    ]
    for item in report["objects"][:20]:
        lines.append(f"- `{item['bucket']}/{item['path']}` | {item.get('size_bytes') or 0} bytes | {item['recommendation']['action']}")
    return "\n".join(lines) + "\n"


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Audit and plan image optimization work.")
    sub = root.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Audit local repo images.")
    audit.add_argument("--root", default=".")
    audit.add_argument("--json-output")
    audit.add_argument("--markdown-output")

    plan = sub.add_parser("plan", help="Build a local conversion plan.")
    plan.add_argument("--root", default=".")
    plan.add_argument("--json-output")
    plan.add_argument("--markdown-output")

    apply = sub.add_parser("apply", help="Apply safe local conversions from a plan.")
    apply.add_argument("--plan", required=True)
    apply.add_argument("--overwrite", action="store_true")
    apply.add_argument("--json-output")
    apply.add_argument("--markdown-output")

    remote = sub.add_parser("supabase-audit", help="Audit image objects in Supabase Storage buckets.")
    remote.add_argument("--url")
    remote.add_argument("--service-key")
    remote.add_argument("--bucket", action="append")
    remote.add_argument("--prefix", default="")
    remote.add_argument("--json-output")
    remote.add_argument("--markdown-output")
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "audit":
        report = local_audit(Path(args.root).resolve())
    elif args.command == "plan":
        report = local_plan(local_audit(Path(args.root).resolve()))
    elif args.command == "apply":
        report = apply_plan(Path(args.plan).resolve(), overwrite=args.overwrite)
    else:
        url = args.url or os.getenv("SUPABASE_URL")
        key = args.service_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise SystemExit("Supabase audit needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or explicit flags.")
        if not args.bucket:
            raise SystemExit("Pass at least one --bucket value.")
        report = supabase_audit(url, key, args.bucket, args.prefix)
    write_json(getattr(args, "json_output", None), report)
    write_md(getattr(args, "markdown_output", None), markdown_report(report))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
