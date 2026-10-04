# IRB-in-Hurry

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)](#testing)
[![Forms](https://img.shields.io/badge/IRB%20forms-43%2F43-brightgreen.svg)](#form-coverage)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Automated IRB document preparation for [KFSYSCC](https://www.kfsyscc.org/) (Koo Foundation Sun Yat-Sen Cancer Center).

Fill in a YAML config with your study details, run one command, and get all required IRB submission forms as Word documents — ready to sign and submit.

[繁體中文版 README](README.zh-TW.md)

---

## Why This Exists

The Institutional Review Board (IRB) is one of the most important inventions in the history of medical research. Born from the ashes of the Nuremberg Trials (1947) and codified through the Declaration of Helsinki (1964) and the Belmont Report (1979), the IRB exists to ensure that no human being is subjected to research without informed consent, proper risk assessment, and ethical oversight. These are non-negotiable principles. The horrors of Tuskegee, Unit 731, and countless other episodes of unchecked medical experimentation remind us why.

**But somewhere along the way, the bureaucracy ate the mission.**

What was meant to protect human subjects has calcified into a paperwork marathon. At [KFSYSCC](https://www.kfsyscc.org/human/common_files/1) alone, researchers must navigate **11 submission categories** and **43+ forms** — each with its own version number, formatting requirements, and checkbox conventions. A single retrospective chart review (minimal risk, no patient contact, de-identified data) requires 5 forms. A clinical trial? Double that. An amendment to fix a typo in your protocol? Another 4 forms.

The researcher's time is finite. Every hour spent copying IRB numbers into the header of form SF037 is an hour not spent analyzing data, writing manuscripts, or — most importantly — caring for patients. The forms themselves are not the problem. The problem is that filling them out is **mindless, repetitive, error-prone labor** that a machine should do.

This project does not bypass the IRB. It does not skip ethical review. It does not auto-approve anything. It simply fills in the forms that the IRB requires, using the data you provide, so you can focus on the parts that actually require human judgment: study design, risk assessment, and the protection of your participants.

> "The ethics of research is in the design, not the paperwork."

**IRB-in-Hurry: because your time is better spent on science.**

---

## Features

- **11 IRB categories** supported: new case, amendment, continuing review, closure, SAE, IB update, import, suspension, appeal, re-review, and other
- **43 form generators** with automatic selection based on study type and submission phase
- **Smart routing**: retrospective study automatically selects expedited review + consent waiver forms
- **DOCX generation** using python-docx with proper formatting (standard KaiTi font, ■/□ checkboxes)
- **PDF + PNG preview** pipeline for visual validation
- **Plain-text checklist** (■/□) tracking both generated forms and manual steps
- **Color-coded dashboard** for submission status overview
- **Claude Code skill** for AI-assisted form preparation

## Form Coverage

All forms from the [KFSYSCC IRB website](https://www.kfsyscc.org/human/common_files/1) are implemented:

| Category | Chinese | Forms | Status |
|----------|---------|-------|--------|
| New case | [新案審查](https://www.kfsyscc.org/human/common_files/1) | SF001, SF002, SF094, SF003-005 | ■ Complete |
| Re-review | [複審案審查](https://www.kfsyscc.org/human/common_files/2) | SF019 | ■ Complete |
| Amendment | [修正案審查](https://www.kfsyscc.org/human/common_files/3) | SF014, SF015, SF016 | ■ Complete |
| Continuing | [期中審查](https://www.kfsyscc.org/human/common_files/4) | SF030, SF031, SF032 | ■ Complete |
| Closure | [結案審查](https://www.kfsyscc.org/human/common_files/5) | SF036, SF037, SF038, SF023 | ■ Complete |
| SAE | [嚴重不良反應](https://www.kfsyscc.org/human/common_files/6) | SF079, SF044, SF074, SF080, SF024 | ■ Complete |
| IB update | [主持人手冊](https://www.kfsyscc.org/human/common_files/7) | SF082, SF083, SF084, SF085 | ■ Complete |
| Import | [專案進口](https://www.kfsyscc.org/human/common_files/8) | SF066, SF067, SF068, SF093 | ■ Complete |
| Other | [其他表單](https://www.kfsyscc.org/human/common_files/9) | SF076 | ■ Complete |
| Suspension | [計畫暫停](https://www.kfsyscc.org/human/common_files/10) | SF047, SF048 | ■ Complete |
| Appeal | [申覆案審查](https://www.kfsyscc.org/human/common_files/11) | SF077, SF054 | ■ Complete |
| Consent | — | SF062, SF063, SF075, SF090, SF091, SF092 | ■ Complete |

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
| `make all` | Generate DOCX + PDF + layout check + dashboard |
| `make templates` | Download official blank forms from kfsyscc.org (once) |
| `make validate` | Layout/font safety gate (A4, 標楷體, Win/Mac, vs official blank) |
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
output/*.docx + templates/official/ (官方空白表單) → validate_layout.py
                                                 → output/layout_report.md
                                                 → output/preview/compare/*.png
```

1. **Edit `config.yml`** — Fill in study metadata (IRB number, titles, PI info, dates, study type)
2. **`make all`** — Generates DOCX forms, converts to PDF, shows dashboard
3. **Layout gate** — `make validate` must report 0 errors; open `output/layout_report.md`
   and `output/preview/compare/*.png` (official blank left, generated right)
4. **Submit the PDF** — fonts are embedded, so it looks identical on Windows and Mac;
   send the DOCX only if the IRB asks to edit it
5. **Complete manual steps** — Sign forms, attach protocol, email to irb@kfsyscc.org

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

## Testing

```bash
make test
```

27 tests covering form selection logic, DOCX content verification, checklist generation, end-to-end generation for both new case and closure phases, and the layout safety gate.

## Dependencies

- Python 3.10+
- [python-docx](https://python-docx.readthedocs.io/) — DOCX generation
- [PyYAML](https://pyyaml.org/) — Config parsing
- [LibreOffice](https://www.libreoffice.org/) — DOCX→PDF conversion (`brew install --cask libreoffice`; Windows: `winget install TheDocumentFoundation.LibreOffice`; Linux: `apt install libreoffice-writer fonts-arphic-ukai`)
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
│   ├── form_selector.py       # 43-form registry + routing
│   ├── generate_all.py        # Main orchestrator
│   ├── checklist.py           # ■/□ checklist generator
│   ├── convert.py             # DOCX→PDF→PNG pipeline
│   ├── fetch_templates.py     # Download official blank forms
│   ├── validate_layout.py     # Layout/font safety gate
│   └── generators/            # One module per IRB category
│       ├── new_case.py        # SF001, SF002, SF094, SF011, SF022
│       ├── consent.py         # SF003-005, SF062, SF063, SF075, SF090-092
│       ├── closure.py         # SF036, SF037, SF038, SF023
│       ├── amendment.py       # SF014, SF015, SF016
│       ├── continuing_review.py # SF030, SF031, SF032
│       ├── sae.py             # SF079, SF044, SF074, SF080, SF024
│       ├── ib_update.py       # SF082, SF083, SF084, SF085
│       ├── import_forms.py    # SF066, SF067, SF068, SF093
│       ├── suspension.py      # SF047, SF048
│       ├── appeal.py          # SF077, SF054
│       ├── re_review.py       # SF019
│       └── other.py           # SF076
├── .claude/skills/irb/        # Claude Code skill set
├── tests/                     # pytest suite
└── output/                    # Generated files (gitignored)
```

## References

- [KFSYSCC IRB Forms](https://www.kfsyscc.org/human/common_files/1) — Official form downloads
- [Nuremberg Code (1947)](https://en.wikipedia.org/wiki/Nuremberg_Code) — Foundation of research ethics
- [Declaration of Helsinki (1964)](https://www.wma.net/policies-post/wma-declaration-of-helsinki/) — Ethical principles for medical research
- [The Belmont Report (1979)](https://www.hhs.gov/ohrp/regulations-and-policy/belmont-report/) — Respect, Beneficence, Justice
- [Common Rule (45 CFR 46)](https://www.hhs.gov/ohrp/regulations-and-policy/regulations/45-cfr-46/) — U.S. federal regulations for human subjects research

## License

MIT
