---
name: irb-form-generator
description: Automate KFSYSCC IRB document preparation — generates Word docs for all IRB submission phases (new case, amendment, continuing review, closure, SAE, etc.). Use when user mentions IRB, ethics review, human subjects research, form generation, or KFSYSCC. Triggers on study proposals, IRB submissions, or form filling tasks.
---

# IRB-in-Hurry Skill

Automated KFSYSCC IRB form generation system. Generates DOCX forms from plain-text sources (`config.toml` + referenced `cv.toml` / `中文計畫摘要.md`), converts to PDF/PNG for visual review.

## Quick Start

Users do NOT need to edit config files by hand. Just provide any free-form text:

```
User: "我想做一個回溯性研究，看2018-2023年肺癌免疫治療的甲狀腺功能，大約200人。我是腫瘤內科陳雅文。"
```

Claude will:
1. Save raw text to `raw/`
2. Distill into `config.toml` + `cv.toml` + `中文計畫摘要.md` (see [distill.md](references/distill.md)); run `make check`
3. Ask for any missing required fields (IRB number, dates)
4. Run `make all` + `make review`
5. Show dashboard and review opinions

### Manual alternative

```bash
# If user prefers to edit the sources directly:
make init EXAMPLE=tdxd-her2low   # optional starting point
vim config.toml cv.toml 中文計畫摘要.md
make check && make all
make review
```

## Workflow Overview

When a user provides a study topic, proposal, or any text:

1. **Save raw input** -- Write to `raw/proposal_YYYYMMDD.md`
2. **Distill to config** -- Study type, dates, subjects → `config.toml`; PI/co-PI → `cv.toml`; background/objectives/methods prose → `中文計畫摘要.md` (see [distill.md](references/distill.md)). `make check` must pass
3. **Confirm with user** -- Ask about any missing required fields (IRB number, exact dates)
4. **Generate forms** -- `make all` → DOCX + PDF + PNG previews + dashboard
5. **Run reviewer** -- `make review` → `reviewers/review_*.md`
6. **Layout safety gate** -- `make validate` (part of `make all`; run `make templates` once first).
   Must be 0 errors. Read `output/layout_report.md`, then view `output/preview/compare/*.png`
   (official blank left, generated right) and report any visible drift to the user.
   Remind the user to submit the PDF (fonts embedded → identical on Windows/Mac).
7. **Fix findings** -- Address required revisions from reviewer
8. **Update checklist** -- Track manual steps via `checklist.md`
9. **Cover letter** -- `make generate` also writes `output/IRB_致委員會函稿_<階段>.md`, a formal
   letter to the committee for the email/paper submission. Help the user fill every
   `【請填寫：…】` field; keep the tone 恭敬、具體, never argumentative (esp. appeals).

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

```toml
# config.toml — "@file" / "@file#key" values are replaced by that file's content
phase    = "new"               # new | amendment | continuing | closure | sae | ...
pi       = "@cv.toml#pi"       # [pi] name, name_en, dept, phone, email
co_pi    = "@cv.toml#co_pi"    # [[co_pi]] entries (optional)
proposal = "@中文計畫摘要.md"   # ## 研究背景 / 研究目的 / 納入條件 / 統計分析 ...

[study]
irb_no      = ""               # IRB case number (blank until assigned)
title_zh    = ""
title_en    = ""
type        = "retrospective"  # retrospective | prospective | clinical_trial | genetic
review_type = "expedited"      # exempt | expedited | full_board
drug_device = false
genetic     = false
multicenter = false

[dates]
study_start = ""
study_end   = ""

[subjects]
planned_n      = 0
consent_waiver = false
```

Phase switches never re-dump the file: `make closure` == `make all PHASE=closure` (one-off);
`make set-phase PHASE=closure` persists it by editing only the `phase =` line.

See [config-schema.md](references/config-schema.md) for the complete field reference.

## Checkbox Convention

- `check(True)` returns **U+25A0** (filled square) = checked/yes
- `check(False)` returns **U+25A1** (empty square) = unchecked/no

All forms use this convention via `docx_utils.check()`.

## Project Structure

```
config.toml                    # Study metadata (single source of truth)
cv.toml                        # Study team (@cv.toml#pi, @cv.toml#co_pi)
中文計畫摘要.md                 # Proposal prose (@中文計畫摘要.md)
examples/                      # Complete example studies (make init EXAMPLE=...)
scripts/
  config.py                   # config.toml loader: @references, Markdown, validation (ConfigError lists every problem)
  docx_utils.py               # Shared DOCX helpers (init_doc, add_p, add_ct, etc.)
  form_selector.py            # Phase + study type -> required forms
  generate_all.py             # Main orchestrator (--phase, --output, --verbose)
  set_phase.py                # Persist phase in config.toml, keeping comments
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
- [Config Schema](references/config-schema.md) -- All config.toml fields and `@` references
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
