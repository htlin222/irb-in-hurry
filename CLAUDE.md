# IRB-in-Hurry

Automated KFSYSCC IRB document preparation system.

## Quick Start

```bash
# Edit config.yml with study details
make templates                    # Once: download official blank forms
make all                          # Generate + PDF + layout gate + dashboard
```

## Conventions

- **Python**: Managed by `uv` (pyproject.toml), run via `uv run` or `make`
- **Font**: 標楷體 (DFKai-SB) for all form text
- **Checkbox**: ■ (U+25A0) = checked, □ (U+25A1) = unchecked
- **Config**: All study data in `config.yml`, never hardcoded
- **Output**: DOCX → `output/`, PDF → `output/`, PNG previews → `output/preview/`
- **Forms**: Named `IRB_SFXXX_中文名稱.docx`
- **Page**: A4 + official per-form margins (`OFFICIAL_MARGINS` in docx_utils), applied by `generate_all`
- **Layout gate**: `make validate` must show 0 errors before submission; PDF is the submission copy

## Project Structure

- `scripts/config.py` — Load + validate `config.yml`; required fields, enums, real booleans, defaults for optional sections
- `scripts/docx_utils.py` — Shared DOCX helper functions (`form_filename` for output names)
- `scripts/form_selector.py` — Phase + study type → required forms
- `scripts/generators/` — One module per IRB category
- `scripts/generate_all.py` — Main orchestrator (`--phase`, `--output`, `--verbose`)
- `scripts/set_phase.py` — Switch `phase:` in config.yml without losing comments
- `scripts/checklist.py` — ■/□ checklist generator
- `scripts/convert.py` — DOCX→PDF→PNG pipeline
- `scripts/fetch_templates.py` — Download official blank forms → `templates/official/`
- `scripts/validate_layout.py` — Layout/font safety gate → `output/layout_report.md`
- `.claude/skills/irb/` — Claude Code skill set

## Testing

```bash
cp tests/fixtures/sample_retrospective.yml config.yml
make all
make test   # every fixture × every phase, config validation, layout gate
make lint   # ruff; CI runs both on every PR
```

New generator: add it to `FORM_REGISTRY` in `form_selector.py`; the e2e matrix
picks it up automatically. New config field: document it in
`.claude/skills/irb/references/config-schema.md`, and add it to `DEFAULTS` /
`BOOL_FIELDS` in `scripts/config.py` if generators index it directly.
