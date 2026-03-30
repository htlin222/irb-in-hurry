---
name: irb-form-generator
description: Automate KFSYSCC IRB document preparation — generates Word docs for all IRB submission phases (new case, amendment, continuing review, closure, SAE, etc.). Use when user mentions IRB, ethics review, human subjects research, form generation, or KFSYSCC. Triggers on study proposals, IRB submissions, or form filling tasks.
---

# IRB-in-Hurry Skill

Automated KFSYSCC IRB form generation system. Generates DOCX forms from `config.yml`, converts to PDF/PNG for visual review.

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
6. **Visual validation** -- Read `output/preview/*.png` to verify layout
7. **Fix findings** -- Address required revisions from reviewer
8. **Update checklist** -- Track manual steps via `checklist.md`

## Study Type Classification

| Study Type | Review Type | Key Config Flags |
|---|---|---|
| Retrospective chart review | expedited | `type: retrospective`, `consent_waiver: true` |
| Prospective observational | expedited or full_board | `type: prospective` |
| Clinical trial (drug) | full_board | `type: clinical_trial`, `drug_device: true` |
| Clinical trial (device) | full_board | `type: clinical_trial`, `drug_device: true` |
| Genetic research | full_board | `type: genetic`, `genetic: true` |
| Multi-center study | varies | `multicenter: true` |

See [study-types.md](references/study-types.md) for the full decision tree.

## Phase to Forms Mapping

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

The form selector (`scripts/form_selector.py`) automatically adds conditional forms based on study type, review type, and config flags.

## Config Schema (Key Fields)

```yaml
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
config.yml                     # Study metadata (single source of truth)
scripts/
  docx_utils.py               # Shared DOCX helpers (init_doc, add_p, add_ct, etc.)
  form_selector.py            # Phase + study type -> required forms
  generate_all.py             # Main orchestrator
  checklist.py                # Generates checklist.md with status
  convert.py                  # DOCX -> PDF -> PNG pipeline
  generators/
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

## Form Details by Category

- [New Case (新案審查)](references/new-case.md) -- SF001, SF002, SF094, SF003-005
- [Closure (結案審查)](references/closure.md) -- SF036, SF037, SF038, SF023
- [Amendment (修正案審查)](references/amendment.md) -- SF014, SF015, SF016
- [Continuing Review (期中審查)](references/continuing-review.md) -- SF030, SF031, SF032
- [SAE & Non-compliance (嚴重不良反應)](references/sae.md) -- SF079, SF044, SF074, SF080, SF024
- [Other Categories](references/other-categories.md) -- IB update, import, suspension, appeal
- [Study Types & Routing](references/study-types.md) -- Classification logic
- [Config Schema](references/config-schema.md) -- All config.yml fields
- [Brainstorm](references/brainstorm.md) -- Research topic ideas tailored to KFSYSCC + Taiwan epidemiology
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

Each generator function follows this signature:

```python
def generate_sfXXX(config: dict, output_dir: str) -> str:
    """Generate SFXXX form. Returns output file path."""
    doc = init_doc()
    # ... build document ...
    path = os.path.join(output_dir, "SFXXX_中文名稱.docx")
    doc.save(path)
    return path
```

Register in `FORM_REGISTRY` in `scripts/form_selector.py`, then add to the appropriate phase in `PHASE_FORMS`.

## Submission

- Electronic: email to irb@kfsyscc.org
- Paper: 1 original + 1 copy to IRB office (B1 administrative building)
- Signed forms require PI wet signature before submission
