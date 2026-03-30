---
name: new-case-forms
description: Detail on new case (新案審查) IRB forms — SF001, SF002, SF094, SF003, SF004, SF005 and conditional forms.
---

# New Case Forms (新案審查)

Phase: `new`. Initial IRB submission for a new research protocol.

## Base Forms (always required)

### SF001 -- 新案審查送審資料表

Cover sheet listing all submitted documents with checkboxes.

- **Config fields**: `study.irb_no`, `study.title_zh`, `study.title_en`, `pi.name`, `pi.dept`
- **Auto-filled**: Document list based on which forms are selected
- **Manual input**: Sponsor name (if applicable), attachments list

### SF002 -- 研究計畫申請書

Main application form with study details, objectives, methods, risk assessment.

- **Config fields**: `study.*`, `pi.*`, `co_pi`, `dates.*`, `subjects.*`
- **Auto-filled**: Header info, PI details, study dates, enrollment numbers, study type checkboxes
- **Manual input**: Study objectives, methodology, risk-benefit analysis, references

### SF094 -- 顯著財務利益申報表

Financial conflict of interest disclosure. Required for all submissions.

- **Config fields**: `pi.name`, `pi.dept`, `study.irb_no`
- **Auto-filled**: PI info, IRB number
- **Manual input**: Financial interest declarations (most studies: check "no" for all items)

## Conditional Forms

### SF003 -- 簡易審查範圍檢核表

Added when `review_type: expedited`. Checklist for expedited review eligibility.

- **Config fields**: `study.type`, `study.review_type`
- **Auto-filled**: Category checkboxes based on study type
- **Manual input**: Justification for expedited review category

### SF004 -- 免予審查範圍檢核表

Added when `review_type: exempt`. Checklist for exempt review eligibility.

- **Config fields**: `study.type`, `study.review_type`
- **Auto-filled**: Exemption category checkboxes
- **Manual input**: Justification for exemption

### SF005 -- 免取得知情同意檢核表

Added when `consent_waiver: true`. Justification for waiving informed consent.

- **Config fields**: `subjects.consent_waiver`, `study.type`
- **Auto-filled**: Waiver criteria checkboxes (retrospective studies auto-check applicable items)
- **Manual input**: Detailed justification for each waiver criterion

### SF062 -- 受試者同意書（臨床研究）

Added when `consent_waiver: false` and `drug_device: false`. Standard consent form.

- **Manual input**: Full consent document content

### SF063 -- 受試者同意書（臨床試驗）

Added when `consent_waiver: false` and `drug_device: true`. Clinical trial consent form.

- **Manual input**: Full consent document with drug/device-specific sections

### SF075 -- 受試者同意書（基因研究）

Added when `genetic: true`. Genetic research consent form.

- **Manual input**: Genetic data handling, future use clauses

### SF090 -- 受試者同意書（藥品試驗）

Added alongside SF063 for drug trials. Drug-specific consent supplement.

### SF091 -- 受試者同意書（兒童）

Added when `vulnerable_population: true`. Assent form for minors.

### SF022 -- 資料及安全性監測計畫

Added when `review_type: full_board`. Data and Safety Monitoring Plan.

- **Manual input**: Monitoring procedures, stopping rules, DSMB composition

## Typical Combinations

| Study Type | Forms |
|---|---|
| Retrospective chart review | SF001, SF002, SF094, SF003, SF005 |
| Prospective observational (with consent) | SF001, SF002, SF094, SF003, SF062 |
| Clinical trial (drug) | SF001, SF002, SF094, SF022, SF063, SF090 |
| Genetic study | SF001, SF002, SF094, SF022, SF062, SF075 |
