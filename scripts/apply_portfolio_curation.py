"""Apply reviewed factual metadata, cover choices, and source-order sequencing."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "projects.json"
CURATION = ROOT / "data" / "portfolio-curation.json"
JS_DATA = ROOT / "js" / "projects-data.js"
REPORT = ROOT / "reports" / "portfolio-import-latest.json"


def image_number(image: dict) -> int:
    match = re.search(r"-(\d+)\.webp$", image["src"])
    return int(match.group(1)) if match else 999999


projects = json.loads(DATA.read_text(encoding="utf-8"))
curation = json.loads(CURATION.read_text(encoding="utf-8"))
portfolio_order = {slug: reviewed.get("portfolioOrder", 999999) for slug, reviewed in curation.items()}
for project in projects:
    reviewed = curation.get(project["slug"], {})
    cover_name = reviewed.pop("cover", None)
    reviewed_order = reviewed.pop("order", None)
    reviewed.pop("portfolioOrder", None)
    project.update(reviewed)
    gallery = sorted(project["galleryImages"], key=image_number)
    if reviewed_order:
        by_name = {Path(image["src"]).name: image for image in gallery}
        if len(reviewed_order) != len(gallery) or set(reviewed_order) != set(by_name):
            raise ValueError(f"Reviewed order for {project['slug']} must contain every gallery image exactly once")
        gallery = [by_name[name] for name in reviewed_order]
    for image in gallery:
        image["aspectRatio"] = round(image["width"] / image["height"], 4)
    if cover_name:
        cover = next((image for image in gallery if image["src"].endswith("/" + cover_name)), None)
        if cover is None:
            raise ValueError(f"Missing reviewed cover {cover_name} for {project['slug']}")
        gallery.remove(cover)
        gallery.insert(0, cover)
    project["galleryImages"] = gallery
    project["coverIndex"] = 0
    project["coverImage"] = gallery[0]

projects.sort(key=lambda project: portfolio_order.get(project["slug"], 999999))

DATA.write_text(json.dumps(projects, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
JS_DATA.write_text("// Generated from data/projects.json by scripts/apply_portfolio_curation.py.\nwindow.ETC_PROJECTS=" + json.dumps(projects, separators=(",", ":"), ensure_ascii=False) + ";\n", encoding="utf-8")
if REPORT.exists():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    project_by_slug = {project["slug"]: project for project in projects}
    for outcome in report.get("projects", []):
        project = project_by_slug.get(outcome["slug"])
        if project:
            outcome["category"] = project["category"]
            outcome["coverImage"] = project["coverImage"]["src"]
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Applied reviewed curation to {len(projects)} projects.")
