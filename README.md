# ETC_PHOTOS V2

A fully local, static redesign of ETC_PHOTOS. Nothing in this directory is connected to the production repository or deployed website.

## Local preview

Run a static server from this directory (opening files directly also works, but a server is preferred):

```powershell
python -m http.server 4173
```

Then open `http://localhost:4173/`.

## Structure

- `index.html` — homepage
- `portfolio.html` — editorial work archive
- `project.html?id=...` — reusable project experience driven by project data
- `booking.html` — package and location booking journey
- `links.html` — mobile-first social/QR landing page
- `data/projects.json` — central project data written by the importer
- `js/projects-data.js` — generated static browser mirror of `data/projects.json`
- `portfolio-import/` — ignored local inbox; source copies never leave or get modified by the importer
- `assets/portfolio/` — generated WebP gallery and preview assets
- `scripts/import_portfolio.py` — safe, rerunnable portfolio importer
- `reports/portfolio-import-latest.json` — complete report from the latest run
- `css/` — shared design system and page layouts
- `assets/` — locally hosted ETC_PHOTOS imagery, icons and brand assets

## Importing a portfolio project

1. Export finished photographs and **copy** one project folder into `portfolio-import/`. Its folder name becomes the project name and slug.
2. Optionally add `_project.json` inside that folder for known details. Supported fields are `title`, `category` (`shoot` or `event`), `cover` (a source filename), `featured`, `vehicle`, `event`, `location`, `date`, `year`, `description`, and `alt`. Never add facts that are not known.
3. Ask Codex to inspect and import it. For a direct local run, use the bundled/current Python environment with Pillow:

```powershell
python scripts/import_portfolio.py
```

4. Review `reports/portfolio-import-latest.json`, every generated gallery, the Portfolio filters, and Homepage Featured Work. An uncertain category is written as `null` with `needsReview: true` rather than guessed.
5. Record reviewed titles, covers and featured positions in `data/portfolio-curation.json`, then run `python scripts/apply_portfolio_curation.py`. The authoritative rendered records remain in `data/projects.json`.
6. Keep the inbox copies until the report and website have been verified.

The importer reads only direct project folders inside `portfolio-import`. It does not modify source photographs. It applies EXIF orientation, strips metadata in generated copies, never upscales, and creates quality-88 WebPs with a 2560px maximum long edge plus quality-86 1100px previews. Output uses deterministic names such as `porsche-cayman-001.webp`.

Re-running an unchanged folder skips it using a source fingerprint. A changed folder is rendered into a staging directory and only replaces its generated output after all images succeed. Existing factual project fields are preserved unless `_project.json` explicitly overrides them.

Reviewed cover choices are preserved during changed reimports when the deterministic filename still exists. Run the curation script after adding a new project or intentionally changing a reviewed cover.

For the first verified real import, `python scripts/import_portfolio.py --replace-demo` replaces the audited temporary project entries. The previous demo assets are intentionally retained while the inbox is empty so the current site is not left blank; their exact audit is in `reports/demo-portfolio-audit.json`.

## Safe inbox cleanup

The cleanup command is a dry run unless the exact confirmation phrase is supplied:

```powershell
python scripts/clean_portfolio_import.py
python scripts/clean_portfolio_import.py --confirm "DELETE IMPORT COPIES"
```

It only removes immediate project folders whose resolved parent is this project's `portfolio-import` directory. It cannot target `assets/portfolio`, project data, or photographs elsewhere on the computer. Only run the confirmed form after visual and report verification.

## Before a future deployment

Review canonical URLs and social preview imagery, verify final project metadata and sitemap dates, then run a complete responsive check. GitHub Pages needs no build step.

### Staging and the production custom domain

The local `CNAME` file is intentionally ignored on the `staging` branch so a test GitHub Pages repository cannot claim `etcphotos.co.uk`. The approved production value is retained in `CNAME.production`.

Only when the production deployment is approved, copy `CNAME.production` to `CNAME`, force-add that single ignored file with `git add -f CNAME`, commit it on the intended production branch, and then configure GitHub Pages and DNS deliberately.
