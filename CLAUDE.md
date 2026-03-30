# IRB-in-Hurry

Automated KFSYSCC IRB document preparation system.

## Quick Start

```bash
# Edit config.yml with study details
make all                          # Generate + PDF + dashboard
```

## Conventions

- **Python**: Managed by `uv` (pyproject.toml), run via `uv run` or `make`
- **Font**: 標楷體 (DFKai-SB) for all form text
- **Checkbox**: ■ (U+25A0) = checked, □ (U+25A1) = unchecked
- **Config**: All study data in `config.yml`, never hardcoded
- **Output**: DOCX → `output/`, PDF → `output/`, PNG previews → `output/preview/`
- **Forms**: Named `IRB_SFXXX_中文名稱.docx`

## Project Structure

- `scripts/docx_utils.py` — Shared DOCX helper functions
- `scripts/form_selector.py` — Phase + study type → required forms
- `scripts/generators/` — One module per IRB category
- `scripts/generate_all.py` — Main orchestrator
- `scripts/checklist.py` — ■/□ checklist generator
- `scripts/convert.py` — DOCX→PDF→PNG pipeline
- `.claude/skills/irb/` — Claude Code skill set

## Testing

```bash
cp tests/fixtures/sample_retrospective.yml config.yml
make all
make test
```
