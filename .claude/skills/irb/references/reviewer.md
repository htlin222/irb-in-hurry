# IRB Reviewer Criteria Reference

## Overview

The simulated reviewer (`irb_in_hurry/reviewer.py`) applies 7 categories of criteria based on 45 CFR 46.111 and institutional standards (KFSYSCC as reference); submission details come from the active institution profile. Run via `irbh review` after generating forms.

## Review Categories

### 1. Document Completeness (文件完整性)
- All required forms generated for the phase
- IRB number, title, PI name consistent across all forms
- Study dates present and not blank
- Co-PI listed in relevant forms
- Form version footers present

### 2. Informed Consent (知情同意) — 45 CFR 46.116, 46.117
- Consent waiver (SF005) justified for retrospective studies
- Consent form includes all required elements
- PI + IRB contact info in consent
- Signature blocks complete

### 3. Risk-Benefit Assessment (風險效益評估) — 45 CFR 46.111(a)(1-2)
- Risk level matches review type
- Risk minimization strategies described
- Anticipated benefits stated

### 4. Privacy & Confidentiality (隱私與保密) — 45 CFR 46.111(a)(7)
- De-identification method confirmed
- Data encryption confirmed
- Retention period specified
- Authorized personnel documented

### 5. Subject Selection (受試者選取) — 45 CFR 46.111(a)(3)
- Sample size stated
- Vulnerable population flag correct
- Selection equitable

### 6. Study Design (研究設計) — 45 CFR 46.111(a)(1)
- Study type matches form selection
- Data period covers research scope
- Design description consistent

### 7. Administrative Compliance (行政合規)
- Financial disclosure (SF094) included
- Signature blocks present
- Current form versions used
- Submission email noted

## Review Decisions (Taiwan Standard)

| Decision | Chinese | When |
|----------|---------|------|
| Approved | 核准 | No required revisions |
| Approved with revisions | 修改後核准 | 1-3 required items |
| Tabled | 擱置 | >3 required items |
| Disapproved | 否決 | Fundamental flaws |

## Finding Severity

| Level | Chinese | Meaning |
|-------|---------|---------|
| Required | 必須修正 | Must fix before submission |
| Suggestion | 建議修改 | Advisory, not blocking |
| Note | 備註 | Informational |

## Placeholder Detection

The reviewer scans for incomplete content patterns: `請填寫`, `＿＿`, `__`, `（請說明）`, `placeholder`, `TODO`, `TBD`

## Usage

```bash
irbh all        # Generate forms
irbh review     # Run reviewer → reviewers/review_*.md
cat reviewers/review_*.md  # Read opinions
```
