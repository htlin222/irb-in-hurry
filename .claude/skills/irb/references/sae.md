---
name: sae-forms
description: Detail on SAE and non-compliance (嚴重不良反應/不遵從事件) IRB forms — SF079, SF044, SF074, SF080, SF024.
---

# SAE & Non-compliance Forms (嚴重不良反應)

Phase: `sae`. Filed when serious adverse events or protocol deviations occur.

## SAE Reporting Forms

### SF079 -- 嚴重不良反應事件審查送審資料表

Cover sheet for SAE submission.

- **Config fields**: `study.irb_no`, `study.title_zh`, `pi.name`
- **Auto-filled**: Header block, document checklist
- **Manual input**: None

### SF044 -- 嚴重不良反應事件通報表（本院）

SAE report for events occurring at our site (KFSYSCC).

- **Config fields**: `study.*`, `pi.*`
- **Auto-filled**: Header info
- **Manual input**: Event description, onset date, severity, causality assessment, outcome, corrective actions

### SF074 -- 嚴重不良反應事件通報表（他院）

SAE report for events occurring at other sites (multi-center studies).

- **Config fields**: `study.*`, `pi.*`
- **Auto-filled**: Header info
- **Manual input**: Reporting site info, event details, relevance to our site

## Non-compliance Forms

### SF080 -- 試驗不遵從事件審查送審資料表

Cover sheet for protocol deviation/non-compliance submission.

- **Config fields**: `study.irb_no`, `study.title_zh`, `pi.name`
- **Auto-filled**: Header block
- **Manual input**: None

### SF024 -- 試驗不遵從事件報告表

Detailed protocol deviation report.

- **Config fields**: `study.*`, `pi.*`
- **Auto-filled**: Header info
- **Manual input**: Deviation description, root cause, corrective and preventive actions (CAPA)

## Notes

- SAE reports must be submitted within 7 days of PI awareness for fatal/life-threatening events, 15 days for others
- SF044 (our site) is the default; SF074 (other site) is used for multi-center SAE notifications
- Non-compliance reports (SF080 + SF024) are separate from SAE reports but use the same phase
- All SAE forms require substantial manual input due to event-specific content
