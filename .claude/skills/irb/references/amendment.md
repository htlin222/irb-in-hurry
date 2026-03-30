---
name: amendment-forms
description: Detail on amendment (修正案審查) IRB forms — SF014, SF015, SF016.
---

# Amendment Forms (修正案審查)

Phase: `amendment`. Filed when changes are made to an approved protocol.

## Forms

### SF014 -- 修正案審查送審資料表

Cover sheet for amendment submission.

- **Config fields**: `study.irb_no`, `study.title_zh`, `study.title_en`, `pi.name`, `pi.dept`
- **Auto-filled**: Header block, document checklist
- **Manual input**: None (fully auto-generated)

### SF015 -- 修正案申請表

Amendment application describing the nature and rationale of changes.

- **Config fields**: `study.*`, `pi.*`, `amendment.*`
- **Auto-filled**: Header info, change description, impact flags (affects consent, affects risk)
- **Manual input**: Detailed rationale for each change, impact assessment

### SF016 -- 修正前後對照表

Before/after comparison table showing exact changes. This form requires the most manual work.

- **Config fields**: `study.irb_no`, `study.title_zh`
- **Auto-filled**: Header info, table structure
- **Manual input**: Original text vs revised text for each change (tracked changes format)

### SF094 -- 顯著財務利益申報表

Financial disclosure (always included with amendments).

## Amendment-Specific Config

```yaml
amendment:
  change_description: "Modified inclusion criteria to expand age range"
  affects_consent: false    # Does the change require consent form update?
  affects_risk: false       # Does the change alter subject risk?
```

## Conditional Forms

- **SF011** (臨床試驗許可證明): Added when `drug_device: true` -- updated trial certificate

## Notes

- SF016 is the most labor-intensive form; it requires manually copying the exact before/after text for each protocol change
- If `affects_consent: true`, a revised consent form (SF062/SF063) must also be submitted
- If `affects_risk: true`, the IRB may require full board re-review
