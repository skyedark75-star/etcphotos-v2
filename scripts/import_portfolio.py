"""Safely turn project folders in portfolio-import into static WebP projects."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps, ImageStat

ROOT = Path(__file__).resolve().parents[1]
INBOX = (ROOT / "portfolio-import").resolve()
ASSETS = (ROOT / "assets" / "portfolio").resolve()
DATA = ROOT / "data" / "projects.json"
JS_DATA = ROOT / "js" / "projects-data.js"
REPORT = ROOT / "reports" / "portfolio-import-latest.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
EVENT_WORDS = {"event", "meet", "show", "festival", "coffee", "concours", "rally"}


def inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def slugify(name: str) -> str:
    value = name.casefold().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    if not value:
        raise ValueError(f"Folder name {name!r} cannot form a URL-safe slug")
    return value


def title_from_folder(name: str) -> str:
    return re.sub(r"[-_]+", " ", name).strip().title()


def classify(name: str, override: str | None) -> tuple[str | None, bool]:
    if override in {"shoot", "event"}:
        return override, False
    words = set(re.findall(r"[a-z0-9]+", name.casefold()))
    if words & EVENT_WORDS:
        return "event", False
    # A conservative vehicle-shoot heuristic: a make/model-like name with 2+ tokens.
    if len(words) >= 2 and not words & {"photos", "portfolio", "misc", "selection"}:
        return "shoot", False
    return None, True


def fingerprint(files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        stat = path.stat()
        digest.update(path.name.casefold().encode())
        digest.update(str(stat.st_size).encode())
        digest.update(str(stat.st_mtime_ns).encode())
    return digest.hexdigest()


def image_score(image: Image.Image) -> float:
    width, height = image.size
    thumbnail = image.convert("RGB")
    thumbnail.thumbnail((320, 320))
    stats = ImageStat.Stat(thumbnail)
    brightness = sum(stats.mean) / 3
    contrast = sum(stats.stddev) / 3
    exposure = max(0, 1 - abs(brightness - 125) / 125)
    landscape = 1.15 if width >= height else 1.0
    return width * height * landscape * (0.65 + 0.2 * exposure + min(contrast, 75) / 500)


def orient(width: int, height: int) -> str:
    ratio = width / height
    return "landscape" if ratio > 1.12 else "portrait" if ratio < 0.89 else "square"


def resized(image: Image.Image, long_edge: int) -> Image.Image:
    copy = image.copy()
    if max(copy.size) > long_edge:
        ratio = long_edge / max(copy.size)
        copy = copy.resize((round(copy.width * ratio), round(copy.height * ratio)), Image.Resampling.LANCZOS)
    return copy


def load_config(folder: Path) -> dict:
    config_path = folder / "_project.json"
    if not config_path.exists():
        return {}
    value = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("_project.json must contain a JSON object")
    return value


def load_projects() -> list[dict]:
    if not DATA.exists():
        return []
    value = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("data/projects.json must contain a JSON array")
    return value


def write_data(projects: list[dict]) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(projects, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    payload = json.dumps(projects, separators=(",", ":"), ensure_ascii=False)
    JS_DATA.write_text("// Generated from data/projects.json by scripts/import_portfolio.py.\nwindow.ETC_PROJECTS=" + payload + ";\n", encoding="utf-8")


def process_project(folder: Path, existing: dict | None, force: bool = False) -> tuple[dict, dict]:
    if not inside(folder, INBOX):
        raise ValueError("Refusing to read outside portfolio-import")
    config = load_config(folder)
    slug = slugify(folder.name)
    files = sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.casefold() in IMAGE_EXTENSIONS), key=lambda p: p.name.casefold())
    if not files:
        raise ValueError("No supported photographs found")
    source_size = sum(p.stat().st_size for p in files)
    digest = fingerprint(files)
    prior_manifest = ASSETS / slug / "manifest.json"
    if not force and prior_manifest.exists() and json.loads(prior_manifest.read_text(encoding="utf-8")).get("fingerprint") == digest:
        return existing or {}, {"slug": slug, "status": "skipped", "detected": len(files), "processed": 0, "failed": 0, "sourceBytes": source_size, "optimisedBytes": sum(p.stat().st_size for p in (ASSETS / slug).rglob("*.webp"))}

    staging = ASSETS / f".staging-{slug}"
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "previews").mkdir(parents=True)
    records = []
    unreadable = []
    try:
        for number, source in enumerate(files, 1):
            try:
                with Image.open(source) as raw:
                    image = ImageOps.exif_transpose(raw).convert("RGB")
                    score = image_score(image)
                    large = resized(image, 2560)
                    preview = resized(image, 1100)
                    filename = f"{slug}-{number:03d}.webp"
                    large.save(staging / filename, "WEBP", quality=88, method=6)
                    preview.save(staging / "previews" / filename, "WEBP", quality=86, method=6)
                    width, height = large.size
                    records.append({"sourceName": source.name, "filename": filename, "width": width, "height": height, "orientation": orient(width, height), "score": score})
            except Exception as error:
                unreadable.append({"file": source.name, "bytes": source.stat().st_size, "reason": str(error)})
        if not records:
            raise ValueError("No readable photographs found")
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    cover_name = config.get("cover")
    if not cover_name and existing and existing.get("coverImage"):
        cover_name = Path(existing["coverImage"].get("src", "")).name or None
    cover_index = next((i for i, record in enumerate(records) if record["sourceName"] == cover_name or record["filename"] == cover_name), None)
    if cover_index is None:
        cover_index = max(range(len(records)), key=lambda i: records[i]["score"])
    cover = records.pop(cover_index)
    # Keep the photographer's deterministic source sequence, moving only the reviewed cover to the lead.
    ordered = [cover, *records]

    category, needs_review = classify(folder.name, config.get("category"))
    title = config.get("title") or (existing or {}).get("title") or title_from_folder(folder.name)
    gallery = []
    for record in ordered:
        gallery.append({
            "src": f"assets/portfolio/{slug}/{record['filename']}",
            "preview": f"assets/portfolio/{slug}/previews/{record['filename']}",
            "width": record["width"], "height": record["height"], "aspectRatio": round(record["width"] / record["height"], 4), "orientation": record["orientation"],
            "alt": config.get("alt") or f"Automotive photograph from {title}"
        })
    preserved = {key: value for key, value in (existing or {}).items() if key not in {"galleryImages", "coverImage", "coverIndex", "temporaryDemo", "sourceFingerprint"}}
    project = {
        **preserved, "id": slug, "slug": slug, "title": title, "category": category,
        "categoryLabel": "Automotive event" if category == "event" else "Automotive shoot" if category == "shoot" else "Needs review",
        "needsReview": needs_review, "featured": config.get("featured", preserved.get("featured", False)),
        "galleryImages": gallery, "coverIndex": 0, "coverImage": gallery[0], "sourceFingerprint": digest
    }
    for optional in ("vehicle", "event", "location", "date", "year", "description"):
        if optional in config:
            project[optional] = config[optional]
    manifest = {"fingerprint": digest, "sourceFolder": folder.name, "files": [{k: v for k, v in item.items() if k != "score"} for item in ordered]}
    (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    target = ASSETS / slug
    backup = ASSETS / f".backup-{slug}"
    if backup.exists():
        shutil.rmtree(backup)
    if target.exists():
        target.rename(backup)
    staging.rename(target)
    shutil.rmtree(backup, ignore_errors=True)
    optimised_size = sum(p.stat().st_size for p in target.rglob("*.webp"))
    return project, {"slug": slug, "status": "processed-with-skips" if unreadable else "processed", "detected": len(files), "processed": len(records) + 1, "skipped": len(unreadable), "failed": 0, "unreadableFiles": unreadable, "sourceBytes": source_size, "optimisedBytes": optimised_size, "category": category, "needsReview": needs_review, "coverImage": gallery[0]["src"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="*", help="Optional folder names or slugs to import")
    parser.add_argument("--replace-demo", action="store_true", help="Remove temporary demo entries after a fully successful real import")
    parser.add_argument("--force", action="store_true", help="Rebuild projects even when the source fingerprint is unchanged")
    args = parser.parse_args()
    INBOX.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    folders = sorted((p for p in INBOX.iterdir() if p.is_dir()), key=lambda p: p.name.casefold())
    if args.slugs:
        wanted = {slugify(value) for value in args.slugs}
        folders = [folder for folder in folders if slugify(folder.name) in wanted]
    existing_projects = load_projects()
    by_slug = {project["slug"]: project for project in existing_projects}
    outcomes, updates, failures = [], {}, []
    for folder in folders:
        slug = slugify(folder.name)
        try:
            project, outcome = process_project(folder, by_slug.get(slug), args.force)
            outcomes.append(outcome)
            if project:
                updates[slug] = project
        except Exception as error:
            failures.append({"slug": slug, "error": str(error)})
            outcomes.append({"slug": slug, "status": "failed", "detected": 0, "processed": 0, "failed": 1})
    if updates and not failures:
        retained = [project for project in existing_projects if project["slug"] not in updates and not (args.replace_demo and project.get("temporaryDemo"))]
        write_data(retained + list(updates.values()))
    source_bytes = sum(item.get("sourceBytes", 0) for item in outcomes)
    optimised_bytes = sum(item.get("optimisedBytes", 0) for item in outcomes)
    report = {
        "createdAt": datetime.now(timezone.utc).isoformat(), "projectsDetected": len(folders),
        "photographsDetected": sum(item.get("detected", 0) for item in outcomes),
        "successfullyProcessed": sum(item.get("processed", 0) for item in outcomes),
        "skipped": sum(item.get("detected", 0) for item in outcomes if item["status"] == "skipped") + sum(item.get("skipped", 0) for item in outcomes),
        "failed": len(failures), "originalBytes": source_bytes, "optimisedBytes": optimised_bytes,
        "sizeReductionPercent": round((1 - optimised_bytes / source_bytes) * 100, 1) if source_bytes else 0,
        "projects": outcomes, "failures": failures,
        "requiresInput": [item["slug"] for item in outcomes if item.get("needsReview")]
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
