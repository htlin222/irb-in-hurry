# IRB-in-Hurry

Institution-agnostic IRB form pipeline: study facts (`config.toml`) + an
institution profile (`institutions/<id>/`) → that institution's official DOCX
forms → PDF → layout gate. KFSYSCC is the reference pack (`institutions/kfsyscc/`).
Method: `docs/METHODOLOGY.md` · Fork guide: `docs/ONBOARDING.md`.

## Quick Start

```bash
# Edit config.toml (facts, `institution = "<id>"`), cv.toml (team), 中文計畫摘要.md (prose)
make check                        # Resolve @references + validate
make templates                    # Once: cache the institution's blank forms
make all                          # Generate + PDF + layout gate + dashboard
make closure                      # = make all PHASE=closure (any phase; file untouched)
make set-phase PHASE=closure      # Persist the phase in config.toml (keeps comments)
make onboard INST=<id>            # New institution: blanks in templates/<id>/ → draft pack
```

## Conventions

- **Python**: Managed by `uv` (pyproject.toml), run via `uv run` or `make`
- **Three kinds of data, never mixed**:
  - study facts → `config.toml` (+ the files it `@`-references)
  - institution facts (names, IRB-no label, submission address, page, margins, font, blank locations) → `institutions/<id>/profile.toml`
  - form list + routing → `institutions/<id>/forms.py`
- **No institution literals in code**: generators read `institution()` (`scripts.docx_utils`); shared scripts read `scripts.institution.current()`
- **Active institution**: `IRB_INSTITUTION` env → `institution` in config.toml → `kfsyscc`
- **Generators**: prefer `template_fill.blank_generator` (fill the official blank); rebuild with python-docx only when a blank can't be filled
- **Font**: the profile's `font` (KFSYSCC: 標楷體 / DFKai-SB); no theme fonts (`pin_form_font`)
- **Checkbox**: ■ (U+25A0) = checked, □ (U+25A1) = unchecked, via `check()`
- **Config (SSOT)**: All study data in plain text, never hardcoded. `config.toml` holds
  structured fields; `"@file"` / `"@file#key"` values inline other files (`@cv.toml#pi`,
  `@中文計畫摘要.md`). Long prose goes in Markdown (`## 標題` → section key), not TOML strings.
  Loader + validation: `scripts/config.py`. Never re-dump config.toml — use `PHASE=` for a
  one-off run, or `set_phase.py` (edits only the `phase =` line) to persist it
- **Output**: DOCX → `output/`, PDF → `output/`, PNG previews → `output/preview/`
- **Page**: profile page size + per-form margins, applied by `generate_all`
- **Blanks**: `templates/<id>/` (gitignored), the gate's ground truth, never edited
- **Layout gate**: `make validate` must show 0 errors before submission; PDF is the submission copy

## Project Structure

- `institutions/<id>/` — profile.toml, forms.py, form_inventory.md (one folder per committee)
- `scripts/institution.py` — Active profile loader
- `scripts/config.py` — config.toml loader (`@` references, Markdown sections, `make check`) + validation: required fields, enums, real booleans, defaults for optional sections
- `scripts/template_fill.py` — Generic fill-the-blank generator (labels → values, □ → ■)
- `scripts/onboard.py` — Blank forms → draft profile + forms.py + inventory
- `scripts/docx_utils.py` — Shared DOCX helpers (profile-aware; `form_filename` for output names)
- `scripts/form_selector.py` — Phase + study type → required forms (active pack); shared `PHASE_NAMES`
- `scripts/generators/` — KFSYSCC rebuild generators (reference pack)
- `scripts/generate_all.py` — Main orchestrator (`--phase`, `--output`, `--verbose`)
- `scripts/set_phase.py` — Persist `phase = "..."` in config.toml without losing comments (`make set-phase`)
- `scripts/checklist.py` — ■/□ checklist generator
- `scripts/convert.py` — DOCX→PDF→PNG pipeline
- `scripts/fetch_templates.py` — Scrape or index official blanks → `templates/<id>/`
- `scripts/validate_layout.py` — Layout/font safety gate → `output/layout_report.md`
- `examples/` — Complete example studies (`make init EXAMPLE=tdxd-her2low`)
- `.claude/skills/irb/` — Claude Code skill set (onboarding: `references/onboard-institution.md`)

## Testing

```bash
make init EXAMPLE=gcsf-retrospective FORCE=1 && make all
make test   # every example × every phase, config validation, layout gate
make lint   # ruff; CI runs both on every PR
```

New generator: add it to `FORM_REGISTRY` in `institutions/<id>/forms.py`; the e2e matrix
picks it up automatically. New config field: document it in
`.claude/skills/irb/references/config-schema.md`, and add it to `DEFAULTS` /
`BOOL_FIELDS` in `scripts/config.py` if generators index it directly.
