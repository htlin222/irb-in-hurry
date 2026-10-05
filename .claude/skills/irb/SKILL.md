---
name: irb-form-generator
description: Institution-agnostic IRB / ethics-committee paperwork pipeline — turns one config.yml into an institution's official DOCX forms (filled or rebuilt), PDFs, a ■/□ checklist and a Win/Mac layout gate, for every submission phase (new case, amendment, continuing review, closure, SAE, etc.). Ships the KFSYSCC form pack; onboards any other institution from its blank Word forms. Use when user mentions IRB, REC, ethics review, human subjects research, filling official DOCX forms, KFSYSCC, or wants to adapt the pipeline to their own hospital's forms.
---

# IRB-in-Hurry Skill

Institution-agnostic IRB form pipeline: `config.yml` (study facts) + an
**institution profile** (`institutions/<id>/`) → official DOCX forms → PDF/PNG →
layout gate. KFSYSCC (`institutions/kfsyscc/`, 43 forms) is the reference pack.

## Step 0: Which institution?

Before anything else, settle which committee the user is submitting to:

| Situation | Action |
|---|---|
| `institution:` in `config.yml` matches the user's committee | proceed |
| Committee has a folder in `institutions/` | set `institution: <id>` in `config.yml` |
| New committee, user has blank forms or a forms URL | follow [onboard-institution.md](references/onboard-institution.md), then return here |
| Unknown | ask: "Which hospital or committee are you submitting to?" |

Everything institution-specific (committee name, IRB-number label, submission
email, paper size, margins, font, form list, routing) comes from
`institutions/<id>/profile.yml` + `forms.py`. **Never hardcode these in scripts
or generators**: read `institution()` (from `scripts.docx_utils`).
Method and invariants: `docs/METHODOLOGY.md`.

## Quick Start

Users do NOT need to manually edit YAML. Just provide any free-form text:

```
User: "我想做一個回溯性研究，看2018-2023年肺癌免疫治療的甲狀腺功能，大約200人。我是腫瘤內科陳雅文。"
```

Claude will:
1. Save raw text to `raw/`
2. Distill into `config.yml` (see [distill.md](references/distill.md))
3. Ask for any missing required fields (IRB number, dates)
4. Run `make all` + `make review`
5. Show dashboard and review opinions

### Manual alternative

```bash
# If user prefers to edit YAML directly:
vim config.yml
make all
make review
```

## Workflow Overview

When a user provides a study topic, proposal, or any text:

1. **Save raw input** -- Write to `raw/proposal_YYYYMMDD.md`
2. **Distill to config** -- Extract study type, PI, dates, subjects → `config.yml` (see [distill.md](references/distill.md))
3. **Confirm with user** -- Ask about any missing required fields (IRB number, exact dates)
4. **Generate forms** -- `make all` → DOCX + PDF + PNG previews + dashboard
5. **Run reviewer** -- `make review` → `reviewers/review_*.md`
6. **Layout safety gate** -- `make validate` (part of `make all`; run `make templates` once first).
   Must be 0 errors. Read `output/layout_report.md`, then view `output/preview/compare/*.png`
   (official blank left, generated right) and report any visible drift to the user.
   Remind the user to submit the PDF (fonts embedded → identical on Windows/Mac).
7. **Fix findings** -- Address required revisions from reviewer
8. **Update checklist** -- Track manual steps via `checklist.md`

## Study Type Classification (generic)

| Study Type | Review Type | Key Config Flags |
|---|---|---|
| Retrospective chart review | expedited | `type: retrospective`, `consent_waiver: true` |
| Prospective observational | expedited or full_board | `type: prospective` |
| Clinical trial (drug) | full_board | `type: clinical_trial`, `drug_device: true` |
| Clinical trial (device) | full_board | `type: clinical_trial`, `drug_device: true` |
| Genetic research | full_board | `type: genetic`, `genetic: true` |
| Multi-center study | varies | `multicenter: true` |

See [study-types.md](references/study-types.md) for the full decision tree.

## Phase to Forms Mapping (KFSYSCC pack)

Phase names are generic; the forms per phase come from the active
institution's `PHASE_FORMS`. For KFSYSCC:

| Phase | Forms | When |
|---|---|---|
| new | SF001, SF002, SF094 + conditional | Initial submission |
| amendment | SF014, SF015, SF016, SF094 | Protocol changes |
| re_review | SF019 | Responding to IRB queries |
| continuing | SF030, SF031, SF023 | Annual review |
| closure | SF036, SF037, SF038, SF023 | Study completion |
| sae | SF079, SF044/SF074, SF080, SF024 | Adverse events |
| ib_update | SF082, SF083 | Investigator's Brochure updates |
| import | SF066, SF067, SF068, SF093 | Drug import |
| suspension | SF047, SF048 | Study pause |
| appeal | SF077, SF054 | Decision appeal |

The form selector (`scripts/form_selector.py`) reads the active institution's `forms_module` and adds conditional forms based on study type, review type, and config flags.

## Config Schema (Key Fields)

```yaml
institution: kfsyscc   # institutions/<id>/profile.yml

study:
  irb_no: ""           # IRB case number
  title_zh: ""         # Chinese title
  title_en: ""         # English title
  type: ""             # retrospective | prospective | clinical_trial | genetic
  review_type: ""      # exempt | expedited | full_board
  drug_device: false   # Drug or device trial
  genetic: false       # Involves genetic data
  multicenter: false   # Multi-center study

pi:
  name: ""             # PI Chinese name
  dept: ""             # Department/title

dates:
  study_start: ""      # Study start date
  study_end: ""        # Study end date

subjects:
  planned_n: 0         # Planned enrollment
  consent_waiver: false # Waiver of informed consent

phase: ""              # new | amendment | continuing | closure | sae | ...
```

See [config-schema.md](references/config-schema.md) for the complete field reference.

## Checkbox Convention

- `check(True)` returns **U+25A0** (filled square) = checked/yes
- `check(False)` returns **U+25A1** (empty square) = unchecked/no

All forms use this convention via `docx_utils.check()`.

## Project Structure

```
config.yml                     # Study metadata (single source of truth) + `institution:`
institutions/<id>/
  profile.yml                  # names, labels, submission, page, font, blanks
  forms.py                     # FORM_REGISTRY + PHASE_FORMS (form pack)
  form_inventory.md            # (onboarded packs) what each blank contains
templates/<id>/                # official blank forms (gitignored ground truth)
scripts/
  institution.py              # active profile loader
  config.py                   # Load + validate config.yml (raises ConfigError listing every problem)
  template_fill.py            # generic fill-the-blank generator
  onboard.py                  # blanks → draft profile/forms/inventory
  docx_utils.py               # Shared DOCX helpers (init_doc, add_p, add_ct, etc.)
  form_selector.py            # Phase + study type -> required forms
  generate_all.py             # Main orchestrator (--phase, --output, --verbose)
  set_phase.py                # Switch phase in config.yml, keeping comments
  checklist.py                # Generates checklist.md with status
  convert.py                  # DOCX -> PDF -> PNG pipeline
  generators/                 # KFSYSCC rebuild generators (reference pack)
    new_case.py               # SF001, SF002, SF094, SF011, SF022
    closure.py                # SF036, SF037, SF038, SF023
    consent.py                # SF003, SF004, SF005, SF062, SF063, SF075, SF090-092
    amendment.py              # SF014, SF015, SF016
    continuing_review.py      # SF030, SF031, SF032
    sae.py                    # SF079, SF044, SF074, SF080, SF024
    ib_update.py              # SF082, SF083, SF084, SF085
    import_forms.py           # SF066, SF067, SF068, SF093
    suspension.py             # SF047, SF048
    appeal.py                 # SF077, SF054
    re_review.py              # SF019
    other.py                  # SF076
output/                        # Generated DOCX and PDF files
output/preview/                # PNG previews for visual validation
checklist.md                   # Auto-generated submission checklist
dashboard.sh                   # Terminal status dashboard
```

## Form Details by Category (KFSYSCC pack)

- [New Case (新案審查)](references/new-case.md) -- SF001, SF002, SF094, SF003-005
- [Closure (結案審查)](references/closure.md) -- SF036, SF037, SF038, SF023
- [Amendment (修正案審查)](references/amendment.md) -- SF014, SF015, SF016
- [Continuing Review (期中審查)](references/continuing-review.md) -- SF030, SF031, SF032
- [SAE & Non-compliance (嚴重不良反應)](references/sae.md) -- SF079, SF044, SF074, SF080, SF024
- [Other Categories](references/other-categories.md) -- IB update, import, suspension, appeal
- [Study Types & Routing](references/study-types.md) -- Classification logic
- [Config Schema](references/config-schema.md) -- All config.yml fields
- [Onboard an Institution](references/onboard-institution.md) -- New committee from its blank DOCX forms
- [Brainstorm](references/brainstorm.md) -- Research topic ideas (KFSYSCC + Taiwan epidemiology example)
- [Distill: Raw Text → Config](references/distill.md) -- How to extract config from free-form text
- [Reviewer Criteria](references/reviewer.md) -- Simulated IRB review checklist
- [Reviewer Guide](references/reviewer-guide.md) -- Rules of thumb, red flags, 45 CFR 46.111 training

## Validation

After generating forms:

1. Run `python scripts/convert.py` to create PDFs and PNG previews
2. Read each `output/preview/*.png` to visually verify layout and content
3. Check `checklist.md` for remaining manual steps (signatures, content sections)
4. Run `./dashboard.sh` for terminal status overview

## Adding New Generators

Prefer **filling the official blank** (layout-exact, a few lines per form):

```python
# institutions/<id>/forms.py
from scripts.template_fill import blank_generator

generate_f01 = blank_generator("F01", fields={
    "計畫名稱": "{study.title_zh}",          # label in the blank → config format string
    "預計收案人數": lambda c: f"{c['subjects']['planned_n']} 人",
}, checks={
    "簡易審查": lambda c: c["study"]["review_type"] == "expedited",
})

FORM_REGISTRY = {"F01": ("新案申請書", "institutions.<id>.forms", "generate_f01")}
```

Rebuild with python-docx only when a blank can't be filled (text boxes,
content controls, PDF-only, generated prose):

```python
def generate_sfXXX(config: dict, output_dir: str) -> str:
    doc = init_doc()                                  # profile page setup + font
    add_p(doc, institution().heading, bold=True)      # never a literal hospital name
    add_header(doc, config)                           # uses institution().irb_no_label
    path = os.path.join(output_dir, f"SFXXX_{config['study']['irb_no']}.docx")
    doc.save(path)
    return path
```

Register it in the institution's `FORM_REGISTRY`. Module paths are relative to
`scripts.` unless they start with `institutions.`. Then add it to `PHASE_FORMS`.

## Submission

Read it from the profile (`submission:` block). `checklist.md` lists it.
For KFSYSCC: email irb@kfsyscc.org; 1 original + 1 copy to the IRB office (B1
administrative building); PI wet signature on signed forms.
