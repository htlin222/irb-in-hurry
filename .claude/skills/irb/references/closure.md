---
name: closure-forms
description: Detail on closure (結案審查) IRB forms — SF036, SF037, SF038, SF023.
---

# Closure Forms (結案審查)

Phase: `closure`. Filed when a study is complete and ready to close.

## Forms

### SF036 -- 結案審查送審資料表

Cover sheet for closure submission. Lists all documents being submitted.

- **Config fields**: `study.irb_no`, `study.title_zh`, `study.title_en`, `pi.name`, `pi.dept`
- **Auto-filled**: Header block, document checklist based on generated forms
- **Manual input**: None (fully auto-generated)

### SF037 -- 結案報告摘要表

Summary table of study outcomes. One-page overview of enrollment, results, and safety.

- **Config fields**: `study.*`, `pi.*`, `dates.*`, `subjects.*`, `closure.*`
- **Auto-filled**: IRB number, study dates, planned vs actual enrollment, subject group breakdown, number of amendments/extensions/SAEs, specimen status
- **Manual input**: PI signature (wet signature required)

### SF038 -- 結案報告書

Detailed closure report. Narrative sections covering study conduct and findings.

- **Config fields**: `study.*`, `dates.*`, `subjects.*`, `closure.*`
- **Auto-filled**: Header info, date ranges, enrollment numbers
- **Manual input**: Study results summary, conclusions, data retention plan details, any deviations during the study

### SF023 -- 資料及安全性監測計畫報告書

Data and Safety Monitoring Plan report. Always included with closure.

- **Config fields**: `study.*`, `subjects.*`, `closure.sae_count`, `closure.data_safety.*`
- **Auto-filled**: Header info, SAE count, data security measures (de-identification, encryption), retention period, authorized personnel
- **Manual input**: Narrative safety summary if SAEs occurred

## Closure-Specific Config

```yaml
closure:
  extensions: 0                    # How many times the study was extended
  amendments: 0                    # Number of protocol amendments
  sae_count: 0                     # Total SAEs during study
  specimens: false                 # Were biological specimens collected?
  data_safety:
    deidentified: true             # Is stored data de-identified?
    encrypted: true                # Is stored data encrypted?
    retention_years: 7             # Years to retain after closure
    authorized_personnel: "PI name" # Who has data access
```

## Retrospective Study Closure

For retrospective chart reviews, closure is typically straightforward:

- `sae_count: 0` (no interventions = no SAEs)
- `specimens: false` (chart review only)
- `consent_waiver: true` already set from initial submission
- SF038 content focuses on data collection completion and findings summary
- SF023 focuses on data security (de-identification, storage, access control)

## Checklist After Generation

The auto-generated `checklist.md` will flag:
- SF038 content sections that need narrative input
- PI signature requirement on SF037
- PDF conversion status
- Submission instructions (email + paper copies)
