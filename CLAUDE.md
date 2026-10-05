# IRB-in-Hurry

Institution-agnostic IRB form pipeline: study facts (`config.yml`) + an
institution profile (`institutions/<id>/`) → that institution's official DOCX
forms → PDF → layout gate. KFSYSCC is the reference pack (`institutions/kfsyscc/`).
Method: `docs/METHODOLOGY.md` · Fork guide: `docs/ONBOARDING.md`.

## Quick Start

```bash
# Edit config.yml with study details (institution: <id>)
make templates                    # Once: cache the institution's blank forms
make all                          # Generate + PDF + layout gate + dashboard
make onboard INST=<id>            # New institution: blanks in templates/<id>/ → draft pack
```

## Conventions

- **Python**: Managed by `uv` (pyproject.toml), run via `uv run` or `make`
- **Three kinds of data, never mixed**:
  - study facts → `config.yml`
  - institution facts (names, IRB-no label, submission address, page, margins, font, blank locations) → `institutions/<id>/profile.yml`
  - form list + routing → `institutions/<id>/forms.py`
- **No institution literals in code**: generators read `institution()` (`scripts.docx_utils`); shared scripts read `scripts.institution.current()`
- **Active institution**: `IRB_INSTITUTION` env → `institution:` in config.yml → `kfsyscc`
- **Generators**: prefer `template_fill.blank_generator` (fill the official blank); rebuild with python-docx only when a blank can't be filled
- **Font**: the profile's `font` (KFSYSCC: 標楷體 / DFKai-SB); no theme fonts (`pin_form_font`)
- **Checkbox**: ■ (U+25A0) = checked, □ (U+25A1) = unchecked, via `check()`
- **Output**: DOCX → `output/`, PDF → `output/`, PNG previews → `output/preview/`
- **Page**: profile page size + per-form margins, applied by `generate_all`
- **Blanks**: `templates/<id>/` (gitignored), the gate's ground truth, never edited
- **Layout gate**: `make validate` must show 0 errors before submission; PDF is the submission copy

## Project Structure

- `institutions/<id>/` — profile.yml, forms.py, form_inventory.md (one folder per committee)
- `scripts/institution.py` — Active profile loader
- `scripts/config.py` — Load + validate `config.yml`; required fields, enums, real booleans, defaults for optional sections
- `scripts/template_fill.py` — Generic fill-the-blank generator (labels → values, □ → ■)
- `scripts/onboard.py` — Blank forms → draft profile + forms.py + inventory
- `scripts/docx_utils.py` — Shared DOCX helpers (profile-aware; `form_filename` for output names)
- `scripts/form_selector.py` — Phase + study type → required forms (active pack); shared `PHASE_NAMES`
- `scripts/generators/` — KFSYSCC rebuild generators (reference pack)
- `scripts/generate_all.py` — Main orchestrator (`--phase`, `--output`, `--verbose`)
- `scripts/set_phase.py` — Switch `phase:` in config.yml without losing comments
- `scripts/checklist.py` — ■/□ checklist generator
- `scripts/convert.py` — DOCX→PDF→PNG pipeline
- `scripts/fetch_templates.py` — Scrape or index official blanks → `templates/<id>/`
- `scripts/validate_layout.py` — Layout/font safety gate → `output/layout_report.md`
- `.claude/skills/irb/` — Claude Code skill set (onboarding: `references/onboard-institution.md`)

## Testing

```bash
cp tests/fixtures/sample_retrospective.yml config.yml
make all
make test   # every fixture × every phase, config validation, layout gate
make lint   # ruff; CI runs both on every PR
```

New generator: add it to `FORM_REGISTRY` in `institutions/<id>/forms.py`; the e2e matrix
picks it up automatically. New config field: document it in
`.claude/skills/irb/references/config-schema.md`, and add it to `DEFAULTS` /
`BOOL_FIELDS` in `scripts/config.py` if generators index it directly.
