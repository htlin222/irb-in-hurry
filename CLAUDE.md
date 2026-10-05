# IRB-in-Hurry

Automated KFSYSCC IRB document preparation system.

## Quick Start

```bash
# Edit config.toml (facts), cv.toml (team), 中文計畫摘要.md (prose)
make check                        # Resolve @references + validate
make templates                    # Once: download official blank forms
make all                          # Generate + PDF + layout gate + dashboard
make closure                      # = make all PHASE=closure (any phase; file untouched)
make set-phase PHASE=closure      # Persist the phase in config.toml (keeps comments)
```

## Conventions

- **Python**: Managed by `uv` (pyproject.toml), run via `uv run` or `make`
- **Font**: 標楷體 (DFKai-SB) for all form text
- **Checkbox**: ■ (U+25A0) = checked, □ (U+25A1) = unchecked
- **Config (SSOT)**: All study data in plain text, never hardcoded. `config.toml` holds
  structured fields; `"@file"` / `"@file#key"` values inline other files (`@cv.toml#pi`,
  `@中文計畫摘要.md`). Long prose goes in Markdown (`## 標題` → section key), not TOML strings.
  Loader + validation: `scripts/config.py`. Never re-dump config.toml — use `PHASE=` for a
  one-off run, or `set_phase.py` (edits only the `phase =` line) to persist it
- **Output**: DOCX → `output/`, PDF → `output/`, PNG previews → `output/preview/`
- **Forms**: Named `IRB_SFXXX_中文名稱.docx`
- **Page**: A4 + official per-form margins (`OFFICIAL_MARGINS` in docx_utils), applied by `generate_all`
- **Layout gate**: `make validate` must show 0 errors before submission; PDF is the submission copy

## Project Structure

- `scripts/config.py` — config.toml loader (`@` references, Markdown sections, `make check`) + validation: required fields, enums, real booleans, defaults for optional sections
- `scripts/docx_utils.py` — Shared DOCX helper functions (`form_filename` for output names)
- `scripts/form_selector.py` — Phase + study type → required forms
- `scripts/generators/` — One module per IRB category
- `scripts/generate_all.py` — Main orchestrator (`--phase`, `--output`, `--verbose`)
- `scripts/set_phase.py` — Persist `phase = "..."` in config.toml without losing comments (`make set-phase`)
- `scripts/checklist.py` — ■/□ checklist generator
- `scripts/convert.py` — DOCX→PDF→PNG pipeline
- `scripts/fetch_templates.py` — Download official blank forms → `templates/official/`
- `scripts/validate_layout.py` — Layout/font safety gate → `output/layout_report.md`
- `examples/` — Complete example studies (`make init EXAMPLE=tdxd-her2low`)
- `.claude/skills/irb/` — Claude Code skill set

## Testing

```bash
make init EXAMPLE=gcsf-retrospective FORCE=1 && make all
make test   # every example × every phase, config validation, layout gate
make lint   # ruff; CI runs both on every PR
```

New generator: add it to `FORM_REGISTRY` in `form_selector.py`; the e2e matrix
picks it up automatically. New config field: document it in
`.claude/skills/irb/references/config-schema.md`, and add it to `DEFAULTS` /
`BOOL_FIELDS` in `scripts/config.py` if generators index it directly.
