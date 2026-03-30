---
name: continuing-review-forms
description: Detail on continuing review (期中審查) IRB forms — SF030, SF031, SF032, SF023.
---

# Continuing Review Forms (期中審查)

Phase: `continuing`. Filed annually for ongoing studies (required before IRB approval expires).

## Forms

### SF030 -- 期中審查送審資料表

Cover sheet for continuing review submission.

- **Config fields**: `study.irb_no`, `study.title_zh`, `study.title_en`, `pi.name`, `pi.dept`
- **Auto-filled**: Header block, document checklist
- **Manual input**: None

### SF031 -- 期中報告書

Progress report covering enrollment, safety, and study status.

- **Config fields**: `study.*`, `pi.*`, `dates.*`, `subjects.*`, `continuing_review.*`
- **Auto-filled**: Header info, enrollment status, deviation count, current enrollment numbers
- **Manual input**: Study progress narrative, interim findings summary

### SF023 -- 資料及安全性監測計畫報告書

Data and Safety Monitoring Plan report (same form used in closure).

- **Config fields**: `study.*`, `subjects.*`, `closure.data_safety.*`
- **Auto-filled**: Safety monitoring data
- **Manual input**: Safety events summary for the review period

### SF032 -- 計畫展延申請表 (conditional)

Added when `continuing_review.extension_requested: true`. Study extension request.

- **Config fields**: `study.*`, `dates.*`
- **Manual input**: Justification for extension, revised timeline

## Continuing Review Config

```yaml
continuing_review:
  enrollment_status: "active"     # active | completed | suspended
  deviations: 0                   # Number of protocol deviations
  extension_requested: false      # Request study period extension
```

## Conditional Forms

- **SF032**: Added when `extension_requested: true`
- **SF011, SF094**: Added when `drug_device: true` (updated certificates and financial disclosure)

## Notes

- Must be submitted at least 30 days before IRB approval expiration
- If the study has completed enrollment but data analysis continues, still requires continuing review
- For multi-year studies, each annual review uses the same phase with updated enrollment and safety data
