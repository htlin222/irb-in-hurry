<!--
  Keywords: IRB form generator, IRB automation, ethics review, human subjects research,
  DOCX form filling, institution-agnostic, KFSYSCC IRB, 和信治癌中心醫院 人體試驗委員會,
  IRB 送審, research ethics paperwork, python-docx
-->

<p align="center">
  <img src="docs/assets/banner.svg" alt="IRB-in-Hurry — institution-agnostic IRB form generator: one YAML file, one command, every official form" width="100%">
</p>

<h1 align="center">IRB-in-Hurry: Institution-Agnostic IRB Form Generator</h1>

<p align="center">
  <strong>Turn one YAML file into a complete, submission-ready IRB packet — DOCX + PDF, in seconds.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
  <a href="#testing"><img src="https://img.shields.io/badge/tests-pytest-brightgreen.svg" alt="Tests: pytest"></a>
  <a href="#form-coverage"><img src="https://img.shields.io/badge/IRB%20forms-43%2F43-brightgreen.svg" alt="IRB forms: 43 of 43"></a>
  <a href="#claude-code-integration"><img src="https://img.shields.io/badge/Claude%20Code-skill-orange.svg" alt="Claude Code skill"></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#bring-your-own-institution">Your Institution</a> ·
  <a href="#form-coverage">Form Coverage</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="README.zh-TW.md">繁體中文</a>
</p>

---

## ⏱️ It's 11:47 PM. The IRB deadline is tomorrow.

You have a brilliant retrospective study. You also have **five Word forms**, each wanting the same IRB number, the same bilingual title, the same PI phone extension, and a very particular opinion about whether a checkbox is ■ or □. You've typed your own name in 標楷體 eleven times tonight. The twelfth time, you misspelled it.

**IRB-in-Hurry** is the colleague who stays late so you don't have to. Describe your study once in `config.yml`, run `make all`, and it:

1. 🧭 **Figures out which forms you need**, based on study type and submission phase
2. 📝 **Fills every one of them in**: headers, titles, checkboxes, dates, and the rest
3. 🖨️ **Exports PDFs** with embedded fonts that look the same on Windows and Mac
4. 🔍 **Checks the layout against the official blank forms** before a reviewer can catch a problem
5. ✅ **Gives you a ■/□ checklist** of what's left (signatures, attachments, the email to the IRB office)

It's an open-source **IRB form generator and research ethics paperwork automation tool** that works with any committee's official Word forms. Everything specific to one institution lives in a small profile folder. It ships with a complete reference pack for the [Koo Foundation Sun Yat-Sen Cancer Center (KFSYSCC, 和信治癌中心醫院)](https://www.kfsyscc.org/) IRB: all **11 submission categories** and **43 official forms**. To use it for your own hospital, drop in your blank `.docx` forms and run `make onboard` ([guide](docs/ONBOARDING.md)).

> It won't do your ethics thinking for you, and that's the point. It does the typing.

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

- **Institution-agnostic**: committee names, IRB-number label, submission address, paper, margins, font and form routing live in `institutions/<id>/`. The pipeline code has no institution literals
- **Bring your own forms**: `make onboard INST=<id>` reads your blank DOCX forms and drafts the profile, label→field map and a form inventory
- **Fill-the-blank engine**: writes values next to the labels of the *official* blank and flips □→■, so layout matches the original exactly
- **11 IRB categories** supported in the KFSYSCC reference pack: new case, amendment, continuing review, closure, SAE, IB update, import, suspension, appeal, re-review, and other
- **43 form generators** with automatic selection based on study type and submission phase
- **Smart routing**: retrospective study automatically selects expedited review + consent waiver forms
- **DOCX generation** using python-docx with proper formatting (standard KaiTi font, ■/□ checkboxes)
- **PDF + PNG preview** pipeline for visual validation
- **Plain-text checklist** (■/□) tracking both generated forms and manual steps
- **Color-coded dashboard** for submission status overview
- **Claude Code skill** for AI-assisted form preparation

## Bring Your Own Institution

```bash
mkdir -p templates/myhosp && cp ~/Downloads/irb-forms/*.docx templates/myhosp/
make onboard INST=myhosp        # → institutions/myhosp/{profile.yml, forms.py, form_inventory.md}
# finish the TODOs (names, email, label→field map, phase routing)
echo "institution: myhosp" >> config.yml
make templates && make all      # generate → PDF → layout gate (0 errors) → dashboard
```

| You provide | The pipeline gives you |
|---|---|
| Your committee's blank `.docx`/`.doc` forms | Paper size, margins, fonts, labels and checkboxes per form, inventoried |
| Names, submission address, phase routing | A `profile.yml` + `forms.py` form pack |
| One `config.yml` per study | Filled forms, PDFs, ■/□ checklist, Win/Mac layout gate |

- **Step-by-step fork guide:** [docs/ONBOARDING.md](docs/ONBOARDING.md)
- **The method and its DOCX invariants:** [docs/METHODOLOGY.md](docs/METHODOLOGY.md)
- **With Claude Code**, say *"onboard my hospital's forms in templates/myhosp"*

## Form Coverage

### KFSYSCC reference pack

All forms from the [KFSYSCC IRB website](https://www.kfsyscc.org/human/common_files/1) are implemented (`institutions/kfsyscc/`):

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
#    Full example with a filled 中文計畫摘要 (T-DXd vs chemo, HER2-low, PSM):
#    cp tests/fixtures/example_tdxd_her2low.yml config.yml

# 3. Generate everything
make all
```

## Usage

### Makefile Commands

| Command | Description |
|---------|-------------|
| `make all` | Generate DOCX + PDF + layout check + dashboard |
| `make templates` | Cache the institution's official blank forms (once) |
| `make onboard INST=<id>` | Draft a new institution from its blanks in `templates/<id>/` |
| `make validate` | Layout/font safety gate (paper, margins, form font, Win/Mac, vs official blank) |
| `make generate` | Generate DOCX forms only |
| `make pdf` | Convert DOCX to PDF + PNG previews |
| `make dashboard` | Show submission status |
| `make checklist` | View ■/□ checklist |
| `make review` | Simulated IRB reviewer on generated forms |
| `make test` | Run pytest |
| `make lint` | Lint with ruff (`make format` auto-fixes) |
| `make clean` | Remove generated files |
| `make new` | Switch to new case phase (edits `phase:` only, comments kept) + generate |
| `make closure` | Switch to closure phase + generate |
| `make amendment` | Switch to amendment phase + generate |
| `make continuing` | Switch to continuing review + generate |

### Workflow

```
config.yml ─┐
institutions/<id>/ (profile + forms) ─┴→ generate_all.py → output/*.docx → convert.py → output/*.pdf
                                                           → output/preview/*.png
                                  checklist.md ← checklist.py
output/*.docx + templates/<id>/ (官方空白表單) → validate_layout.py
                                                 → output/layout_report.md
                                                 → output/preview/compare/*.png
```

1. **Edit `config.yml`** — Fill in study metadata (IRB number, titles, PI info, dates, study type)
2. **`make all`** — Generates DOCX forms, converts to PDF, shows dashboard
3. **Layout gate** — `make validate` must report 0 errors; open `output/layout_report.md`
   and `output/preview/compare/*.png` (official blank left, generated right)
4. **Submit the PDF** — fonts are embedded, so it looks identical on Windows and Mac;
   send the DOCX only if the IRB asks to edit it
5. **Complete manual steps** — Sign forms, attach protocol, send to the address in the profile (KFSYSCC: irb@kfsyscc.org)

### Config Schema

```yaml
institution: kfsyscc         # institutions/<id>/profile.yml

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

### Study Type → Form Selection (KFSYSCC pack)

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

Tests cover form selection, DOCX content, checklist generation, end-to-end generation for new case and closure, the layout safety gate, the institution profile, the fill-the-blank engine, and onboarding from synthetic blanks.

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
├── config.yml                 # Study metadata (single source of truth) + institution:
├── Makefile                   # Easy commands
├── dashboard.sh               # Status overview
├── institutions/
│   └── kfsyscc/               # Reference pack: profile.yml + forms.py (registry + routing)
├── templates/<id>/            # Official blank forms (gitignored)
├── docs/                      # METHODOLOGY.md, ONBOARDING.md
├── scripts/
│   ├── institution.py         # Active institution profile
│   ├── config.py              # Load + validate config.yml (clear errors, defaults)
│   ├── template_fill.py       # Generic fill-the-blank generator
│   ├── onboard.py             # Blanks → draft profile / forms / inventory
│   ├── docx_utils.py          # Shared DOCX helpers
│   ├── form_selector.py       # Phase routing over the active form pack
│   ├── generate_all.py        # Main orchestrator (--phase, --output, --verbose)
│   ├── set_phase.py           # Switch phase in config.yml, keeping comments
│   ├── checklist.py           # ■/□ checklist generator
│   ├── convert.py             # DOCX→PDF→PNG pipeline
│   ├── fetch_templates.py     # Scrape or index official blank forms
│   ├── validate_layout.py     # Layout/font safety gate
│   └── generators/            # KFSYSCC rebuild generators, one module per category
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

## FAQ

**What is IRB-in-Hurry?**
An open-source Python tool that fills in an institution's Institutional Review Board (IRB) submission forms automatically from a single YAML config, producing Word (DOCX) and PDF files ready to sign. It ships with the full KFSYSCC form pack and onboards other institutions from their blank Word forms.

**Does it replace IRB review or ethical judgment?**
No. It never submits, approves, or skips anything. It fills in the paperwork the IRB requires. Study design, risk assessment, and participant protection stay with you and the committee.

**Which IRB submissions are supported?**
For KFSYSCC, all 11 categories: new case (新案), re-review (複審), amendment (修正案), continuing review (期中審查), closure (結案), SAE (嚴重不良反應), IB update, project import, suspension, appeal (申覆), and other forms. That's 43 forms in total.

**Will the forms look right on Windows and Mac?**
Yes. Submit the generated PDF, which has fonts embedded. `make validate` checks paper size, official margins, and the institution's form font (KFSYSCC: 標楷體 / DFKai-SB) against the official blank templates, and it has to report 0 errors before you submit.

**Can I use it for another hospital's IRB?**
Yes, and that is what the design is for. Put your committee's blank forms in `templates/<id>/` and run `make onboard INST=<id>`. Then finish the drafted `institutions/<id>/profile.yml` and `forms.py`. Most forms need only a `label → config field` map, because the engine fills the official blank itself. See [docs/ONBOARDING.md](docs/ONBOARDING.md).

**Does it work with AI assistants?**
Yes. It includes a [Claude Code skill](.claude/skills/irb/SKILL.md) that can classify your study from a proposal, draft `config.yml`, and walk you through the remaining manual steps.

## References

- [KFSYSCC IRB Forms](https://www.kfsyscc.org/human/common_files/1) — Official form downloads
- [Nuremberg Code (1947)](https://en.wikipedia.org/wiki/Nuremberg_Code) — Foundation of research ethics
- [Declaration of Helsinki (1964)](https://www.wma.net/policies-post/wma-declaration-of-helsinki/) — Ethical principles for medical research
- [The Belmont Report (1979)](https://www.hhs.gov/ohrp/regulations-and-policy/belmont-report/) — Respect, Beneficence, Justice
- [Common Rule (45 CFR 46)](https://www.hhs.gov/ohrp/regulations-and-policy/regulations/45-cfr-46/) — U.S. federal regulations for human subjects research

## License

MIT. Free to use, fork, and adapt for your own institution's IRB. PRs that add an `institutions/<id>/` pack are welcome.

---

<p align="center"><sub>Made for researchers who'd rather be doing research. ⏱️ IRB-in-Hurry</sub></p>
