# IRB-in-Hurry

Automated IRB document preparation for [KFSYSCC](https://www.kfsyscc.org/) (Koo Foundation Sun Yat-Sen Cancer Center).

Fill in a YAML config with your study details, run one command, and get all required IRB submission forms as Word documents — ready to sign and submit.

[繁體中文版 README](README.zh-TW.md)

## Features

- **11 IRB categories** supported: new case, amendment, continuing review, closure, SAE, IB update, import, suspension, appeal, re-review, and other
- **44+ form registry** with automatic selection based on study type and submission phase
- **Smart routing**: retrospective study automatically selects expedited review + consent waiver forms
- **DOCX generation** using python-docx with proper formatting (標楷體 font, ■/□ checkboxes)
- **PDF + PNG preview** pipeline for visual validation
- **Plain-text checklist** (■/□) tracking both generated forms and manual steps
- **Color-coded dashboard** for submission status overview
- **Claude Code skill** for AI-assisted form preparation

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/htlin222/irb-in-hurry.git
cd irb-in-hurry
make setup

# 2. Edit config.yml with your study details
#    (or copy the example fixture)
cp tests/fixtures/sample_retrospective.yml config.yml

# 3. Generate everything
make all
```

## Usage

### Makefile Commands

| Command | Description |
|---------|-------------|
| `make all` | Generate DOCX + PDF + dashboard |
| `make generate` | Generate DOCX forms only |
| `make pdf` | Convert DOCX to PDF + PNG previews |
| `make dashboard` | Show submission status |
| `make checklist` | View ■/□ checklist |
| `make test` | Run pytest |
| `make clean` | Remove generated files |
| `make new` | Switch to new case phase + generate |
| `make closure` | Switch to closure phase + generate |
| `make amendment` | Switch to amendment phase + generate |
| `make continuing` | Switch to continuing review + generate |

### Workflow

```
config.yml → generate_all.py → output/*.docx → convert.py → output/*.pdf
                                                           → output/preview/*.png
                                  checklist.md ← checklist.py
```

1. **Edit `config.yml`** — Fill in study metadata (IRB number, titles, PI info, dates, study type)
2. **`make all`** — Generates DOCX forms, converts to PDF, shows dashboard
3. **Review previews** — Check `output/preview/*.png` for visual validation
4. **Complete manual steps** — Sign forms, attach protocol, email to irb@kfsyscc.org

### Config Schema

```yaml
study:
  irb_no: "20250801A"
  title_zh: "研究中文標題"
  title_en: "English Title"
  type: retrospective        # retrospective|prospective|clinical_trial
  review_type: expedited     # exempt|expedited|full_board

pi:
  name: "林協霆"
  dept: "腫瘤內科部／醫師"
  email: "htlin222@kfsyscc.org"

subjects:
  planned_n: 300
  consent_waiver: true       # auto-set for retrospective

phase: new                   # new|amendment|continuing|closure|sae|...
```

See [config-schema reference](.claude/skills/irb/references/config-schema.md) for all fields.

### Study Type → Form Selection

| Study Type | Review | Auto-selected Forms |
|-----------|--------|-------------------|
| Retrospective chart review | Expedited | SF001, SF002, SF094, SF003, SF005 |
| Prospective observational | Expedited/Full | SF001, SF002, SF094, SF062 |
| Clinical trial (drug) | Full board | SF001, SF002, SF094, SF063, SF090, SF022 |
| Genetic research | Full board | SF001, SF002, SF094, SF075 |

## Dependencies

- Python 3.10+
- [python-docx](https://python-docx.readthedocs.io/) — DOCX generation
- [PyYAML](https://pyyaml.org/) — Config parsing
- [LibreOffice](https://www.libreoffice.org/) — DOCX→PDF conversion (`brew install --cask libreoffice`)
- [poppler](https://poppler.freedesktop.org/) — PDF→PNG preview (`brew install poppler`)

## Claude Code Integration

This project includes a [Claude Code skill](.claude/skills/irb/SKILL.md) that enables AI-assisted IRB form preparation. When using Claude Code in this repo, it can:

- Classify your study type from a proposal description
- Auto-fill `config.yml` based on your study details
- Generate and validate all required forms
- Guide you through manual steps

## Project Structure

```
irb-in-hurry/
├── config.yml                 # Study metadata (single source of truth)
├── Makefile                   # Easy commands
├── dashboard.sh               # Status overview
├── scripts/
│   ├── docx_utils.py          # Shared DOCX helpers
│   ├── form_selector.py       # 44-form registry + routing
│   ├── generate_all.py        # Main orchestrator
│   ├── checklist.py           # ■/□ checklist generator
│   ├── convert.py             # DOCX→PDF→PNG pipeline
│   └── generators/            # One module per IRB category
├── .claude/skills/irb/        # Claude Code skill set
├── tests/                     # pytest suite
└── output/                    # Generated files (gitignored)
```

## License

MIT
