# IRB-in-Hurry

Institution-agnostic IRB form pipeline, packaged as `irb-in-hurry` (command `irbh`):
study facts (`config.toml`) + an institution pack (`profile.toml` + `forms.py`) →
that institution's official DOCX forms → PDF → layout gate. KFSYSCC is the bundled
reference pack (`irb_in_hurry/institutions/kfsyscc/`).
Method: `docs/METHODOLOGY.md` · Fork guide: `docs/ONBOARDING.md`.

## Quick Start

The repo root doubles as a study folder. `make <x>` = `uv run irbh <x>`:

```bash
# Edit config.toml (facts, `institution = "<id>"`), cv.toml (team), 中文計畫摘要.md (prose)
make check                        # Resolve @references + validate
make templates                    # Once: cache the institution's blank forms
make all                          # Generate + PDF + layout gate + dashboard
make closure                      # = make all PHASE=closure (any phase; file untouched)
make set-phase PHASE=closure      # Persist the phase in config.toml (keeps comments)
make onboard INST=<id>            # New institution: blanks in templates/<id>/ → draft pack
uv run irbh doctor                # LibreOffice, poppler, form font, config, blanks
```

Installed users run the same commands as `irbh <x>` in any study folder
(`irbh init <example>` starts one and copies `.claude/skills/irb/` into it).

## Conventions

- **Python**: Managed by `uv` (pyproject.toml, hatchling build), run via `uv run irbh` or `make`
- **Package**: all code lives in `irb_in_hurry/` (import `irb_in_hurry.*`, never path hacks);
  data shipped in the wheel (packs, examples, `fonts.conf`) sits inside it, and the skill is
  force-included as `irb_in_hurry/skill`. Paths for study data are relative to the **cwd**
  (the study folder), never to `__file__`
- **New CLI command**: add it to `irb_in_hurry/cli.py` (and a Makefile target if contributors use it)
- **Three kinds of data, never mixed**:
  - study facts → `config.toml` (+ the files it `@`-references)
  - institution facts (names, IRB-no label, submission address, page, margins, font, blank locations) → `<pack>/profile.toml`
  - form list + routing → `<pack>/forms.py`
- **No institution literals in code**: generators read `institution()` (`irb_in_hurry.docx_utils`); shared modules read `irb_in_hurry.institution.current()`
- **Active institution**: `IRB_INSTITUTION` env → `institution` in config.toml → `kfsyscc`
- **Pack lookup** (first wins): `<cwd>/institutions/<id>/` (local, from `irbh onboard`) →
  `irb_in_hurry.institutions` entry points (installed packages) → bundled `irb_in_hurry/institutions/<id>/`
- **Generators**: prefer `template_fill.blank_generator` (fill the official blank); rebuild with python-docx only when a blank can't be filled
- **Font**: the profile's `font` (KFSYSCC: 標楷體 / DFKai-SB); no theme fonts (`pin_form_font`)
- **Checkbox**: ■ (U+25A0) = checked, □ (U+25A1) = unchecked, via `check()`
- **Config (SSOT)**: All study data in plain text, never hardcoded. `config.toml` holds
  structured fields; `"@file"` / `"@file#key"` values inline other files (`@cv.toml#pi`,
  `@中文計畫摘要.md`). Long prose goes in Markdown (`## 標題` → section key), not TOML strings.
  Loader + validation: `irb_in_hurry/config.py`. Never re-dump config.toml — use `PHASE=` for a
  one-off run, or `set_phase.py` (edits only the `phase =` line) to persist it
- **Output**: DOCX → `output/`, PDF → `output/`, PNG previews → `output/preview/`
- **Page**: profile page size + per-form margins, applied by `generate_all`
- **Blanks**: `templates/<id>/` in the study folder (gitignored; `$IRB_TEMPLATES/<id>/` to share), the gate's ground truth, never edited, never packaged
- **Layout gate**: `make validate` must show 0 errors before submission; PDF is the submission copy

## Project Structure

- `irb_in_hurry/cli.py` — `irbh` command (init, check, generate, pdf, templates, onboard, validate, all, dashboard, review, set-phase, institutions, skill, doctor; `irbh <phase>` = `all --phase`)
- `irb_in_hurry/institutions/<id>/` — bundled packs: profile.toml, forms.py (registered as entry points in pyproject.toml)
- `irb_in_hurry/examples/` — Complete example studies (`irbh init <name>` / `make init EXAMPLE=<name>`)
- `irb_in_hurry/institution.py` — Pack lookup (local → installed → bundled) + active profile loader
- `irb_in_hurry/config.py` — config.toml loader (`@` references, Markdown sections, `irbh check`) + validation: required fields, enums, real booleans, defaults for optional sections
- `irb_in_hurry/template_fill.py` — Generic fill-the-blank generator (labels → values, □ → ■)
- `irb_in_hurry/onboard.py` — Blank forms → draft profile + forms.py + inventory in `<cwd>/institutions/<id>/`
- `irb_in_hurry/docx_utils.py` — Shared DOCX helpers (profile-aware; `form_filename` for output names)
- `irb_in_hurry/form_selector.py` — Phase + study type → required forms (active pack); shared `PHASE_NAMES`
- `irb_in_hurry/generators/` — KFSYSCC rebuild generators (reference pack; `generators.*` in a FORM_REGISTRY)
- `irb_in_hurry/generate_all.py` — Main orchestrator
- `irb_in_hurry/set_phase.py` — Persist `phase = "..."` in config.toml without losing comments
- `irb_in_hurry/checklist.py` — ■/□ checklist generator
- `irb_in_hurry/dashboard.py` — Submission status dashboard
- `irb_in_hurry/convert.py` — DOCX→PDF→PNG pipeline
- `irb_in_hurry/fetch_templates.py` — Scrape or index official blanks → `templates/<id>/`
- `irb_in_hurry/validate_layout.py` — Layout/font safety gate → `output/layout_report.md`
- `.claude/skills/irb/` — Claude Code skill set, shipped in the wheel (onboarding: `references/onboard-institution.md`)
- `.github/workflows/release.yml` — tag `vX.Y.Z` (= pyproject version) → GitHub Release (+ PyPI when `PUBLISH_PYPI=true`)

## Testing

```bash
make init EXAMPLE=gcsf-retrospective FORCE=1 && make all
make test   # every example × every phase, config validation, layout gate, CLI
make lint   # ruff; CI runs both on every PR, plus a wheel smoke test outside the repo
make build  # sdist + wheel; install dist/*.whl in a fresh venv to try it as a user
```

New generator: add it to `FORM_REGISTRY` in the pack's `forms.py`; the e2e matrix
picks it up automatically. New config field: document it in
`.claude/skills/irb/references/config-schema.md`, and add it to `DEFAULTS` /
`BOOL_FIELDS` in `irb_in_hurry/config.py` if generators index it directly.
