---
name: config-schema
description: Complete reference for all config.yml fields used by IRB form generators.
---

# Config Schema Reference

All study data lives in `config.yml`. Generators read from this file; nothing is hardcoded.

## `study` (required)

| Field | Type | Description | Example |
|---|---|---|---|
| `irb_no` | string | IRB case number | `"20250801A"` |
| `project_no` | string | Project number (or "不適用") | `"不適用"` |
| `title_zh` | string | Chinese title | `"早期乳癌..."` |
| `title_en` | string | English title | `"Impact of..."` |
| `type` | string | Study type | `retrospective`, `prospective`, `clinical_trial`, `genetic` |
| `design` | string | Study design | `cohort`, `case_control`, `cross_sectional`, `rct` |
| `review_type` | string | IRB review type | `exempt`, `expedited`, `full_board` |
| `drug_device` | bool | Drug or device trial | `false` |
| `genetic` | bool | Involves genetic data | `false` |
| `multicenter` | bool | Multi-center study | `false` |

## `pi` (required)

| Field | Type | Description | Example |
|---|---|---|---|
| `name` | string | PI Chinese name | `"林協霆"` |
| `name_en` | string | PI English name | `"Hsieh-Ting Lin"` |
| `dept` | string | Department and title | `"腫瘤內科部／醫師"` |
| `phone` | string | Contact phone | `"0920476278（院內分機1640）"` |
| `email` | string | Contact email | `"htlin222@kfsyscc.org"` |

## `co_pi` (optional, list)

Each entry:

| Field | Type | Description |
|---|---|---|
| `name` | string | Co-PI Chinese name |
| `name_en` | string | Co-PI English name |
| `dept` | string | Department and title |

## `dates` (required)

| Field | Type | Description | Example |
|---|---|---|---|
| `study_start` | string | Study start date | `"2025年08月01日"` |
| `study_end` | string | Study end date | `"2026年05月31日"` |
| `data_period` | string | Data collection period | `"2013年01月01日 至 2023年12月31日"` |
| `irb_approval_date` | string | IRB approval date | `"2025年07月20日"` |

## `subjects` (required)

| Field | Type | Description | Example |
|---|---|---|---|
| `planned_n` | int | Planned enrollment number | `300` |
| `actual_n` | int | Actual enrolled (for closure/continuing) | `882` |
| `consent_waiver` | bool | Waiver of informed consent | `true` |
| `vulnerable_population` | bool | Includes vulnerable subjects | `false` |
| `groups` | list | Subject groups with `name` and `n` | see below |

### `subjects.groups` (optional, list)

Each entry: `{ name: "Group name", n: 118 }`

## `phase` (required)

One of: `new`, `amendment`, `re_review`, `continuing`, `closure`, `sae`, `ib_update`, `import`, `suspension`, `appeal`

## `closure` (when phase=closure)

| Field | Type | Description |
|---|---|---|
| `extensions` | int | Number of extensions granted |
| `amendments` | int | Number of amendments |
| `sae_count` | int | Number of SAEs during study |
| `specimens` | bool | Biological specimens collected |
| `data_safety.deidentified` | bool | Data is de-identified |
| `data_safety.encrypted` | bool | Data is encrypted |
| `data_safety.retention_years` | int | Years to retain data |
| `data_safety.authorized_personnel` | string | Who can access data |

## `amendment` (when phase=amendment)

| Field | Type | Description |
|---|---|---|
| `change_description` | string | Description of changes |
| `affects_consent` | bool | Changes affect consent form |
| `affects_risk` | bool | Changes affect risk level |

## `continuing_review` (when phase=continuing)

| Field | Type | Description |
|---|---|---|
| `enrollment_status` | string | Current enrollment status |
| `deviations` | int | Number of protocol deviations |
| `extension_requested` | bool | Requesting study extension |
