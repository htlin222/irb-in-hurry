# IRB-in-Hurry

Automated KFSYSCC IRB document preparation system.

## Quick Start

```bash
# Edit config.toml (facts), cv.toml (team), 中文計畫摘要.md (prose)
make check                        # Resolve @references + validate
make templates                    # Once: download official blank forms
make all                          # Generate + PDF + layout gate + dashboard
make closure                      # = make all PHASE=closure (any phase)
```

## Conventions

- **Python**: Managed by `uv` (pyproject.toml), run via `uv run` or `make`
- **Font**: 標楷體 (DFKai-SB) for all form text
- **Checkbox**: ■ (U+25A0) = checked, □ (U+25A1) = unchecked
- **Config (SSOT)**: All study data in plain text, never hardcoded. `config.toml` holds
  structured fields; `"@file"` / `"@file#key"` values inline other files (`@cv.toml#pi`,
  `@中文計畫摘要.md`). Long prose goes in Markdown (`## 標題` → section key), not TOML strings.
  Loader + validation: `scripts/config.py`. Never rewrite config.toml to switch phase — use `PHASE=`
- **Output**: DOCX → `output/`, PDF → `output/`, PNG previews → `output/preview/`
- **Forms**: Named `IRB_SFXXX_中文名稱.docx`
- **Page**: A4 + official per-form margins (`OFFICIAL_MARGINS` in docx_utils), applied by `generate_all`
- **Layout gate**: `make validate` must show 0 errors before submission; PDF is the submission copy

## Project Structure

- `scripts/config.py` — config.toml loader (`@` references, Markdown sections, validation, `make check`)
- `scripts/docx_utils.py` — Shared DOCX helper functions
- `scripts/form_selector.py` — Phase + study type → required forms
- `scripts/generators/` — One module per IRB category
- `scripts/generate_all.py` — Main orchestrator
- `scripts/checklist.py` — ■/□ checklist generator
- `scripts/convert.py` — DOCX→PDF→PNG pipeline
- `scripts/fetch_templates.py` — Download official blank forms → `templates/official/`
- `scripts/validate_layout.py` — Layout/font safety gate → `output/layout_report.md`
- `examples/` — Complete example studies (`make init EXAMPLE=tdxd-her2low`)
- `.claude/skills/irb/` — Claude Code skill set

## Testing

```bash
make test                         # uses examples/*/config.toml
make init EXAMPLE=gcsf-retrospective FORCE=1 && make all
```
