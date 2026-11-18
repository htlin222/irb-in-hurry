---
name: config-schema
description: Complete reference for config.toml, its @file references, and every field used by IRB form generators.
---

# Config Schema Reference

All study data lives in plain text with `config.toml` as the entry point; nothing is
hardcoded. `irbh check` (`irb_in_hurry/config.py`) resolves references, validates required
fields and prints a summary; `--json` prints the fully resolved config.
Institution facts (committee name, IRB-number label, submission address, page,
font) are **not** config: they live in `institutions/<id>/profile.toml`.

## File references (`@`)

Any string value `"@path"` or `"@path#key"` is replaced by that file's content. Paths are
relative to the file containing the reference; referenced files may reference others.

| Target | Result |
|---|---|
| `"@cv.toml#pi"` | the `[pi]` table of `cv.toml` |
| `"@cv.toml"` | the whole TOML document |
| `"@中文計畫摘要.md"` | Markdown with `## headings` → table of sections |
| `"@中文計畫摘要.md#研究背景"` | one section (by key or heading) |
| `"@修正說明.md"` | Markdown without `##` headings → plain text |
| `"@note.txt"` | plain text |

Markdown rules: `## 二、研究背景` → key `background` (numbering ignored, see table under
`proposal`; other headings are used verbatim as keys). A section consisting only of `-` /
`1.` items becomes a list; anything else becomes paragraphs (wrapped lines are joined —
no space next to CJK — and blank lines separate paragraphs). `<!-- comments -->` and the
`# title` line are dropped; `**bold**` / `` `code` `` markers are stripped.

Required (validated): `phase`, `study.title_zh`, `study.title_en`, `study.type`,
`study.review_type`, `pi.name`, `pi.dept`, `dates.study_start`, `dates.study_end`,
`subjects.planned_n`.

## `institution`

| Field | Type | Description | Example |
|---|---|---|---|
| `institution` | string | Folder under `institutions/` whose profile + form pack to use (default `kfsyscc`; `IRB_INSTITUTION` env overrides). Top-level key, before the first `[table]`. | `"kfsyscc"` |

When onboarding a new institution needs a field that isn't listed here, add it
under the matching section below and document it in this file.

## `phase` (required)

One of: `new`, `amendment`, `re_review`, `continuing`, `closure`, `sae`, `ib_update`, `import`, `suspension`, `appeal`
(limited to the phases the institution's form pack routes).

Top-level key (must appear before the first `[table]`). Override per run without editing
the file: `irbh closure` or `irbh all --phase closure`.
To persist a switch, `irbh set-phase closure` (`irb_in_hurry/set_phase.py`) rewrites only
the value on the `phase =` line, keeping its comment and the rest of the file.

## Validation

`irb_in_hurry/config.py` validates the resolved config on load and lists every problem at
once: missing required fields, an unknown `institution`, a `phase` the institution's form
pack doesn't route, unknown `study.type` / `study.review_type`,
sections of the wrong shape (e.g. `pi` resolving to text instead of a table), co-PIs
without a `name`, and quoted booleans (`"false"` is a non-empty string and would count
as true — write `false`). Optional sections (`co_pi`, `closure`, `amendment`,
`continuing_review`) may be omitted entirely; they and optional fields generators index
directly are filled with neutral defaults (`DEFAULTS` / `BOOL_FIELDS` in `irb_in_hurry/config.py`).

## `study` (required)

| Field | Type | Description | Example |
|---|---|---|---|
| `irb_no` | string | IRB case number | `"20250801A"` |
| `project_no` | string | Project number (or "不適用") | `"不適用"` |
| `title_zh` | string | Chinese title | `"早期乳癌..."` |
| `title_en` | string | English title | `"Impact of..."` |
| `type` | string | Study type | `retrospective`, `prospective`, `clinical_trial`, `genetic` |
| `design` | `研究設計` | 五、研究設計 (appended after the generated sentence) |
| `review_type` | string | IRB review type | `exempt`, `expedited`, `full_board` |
| `drug_device` | bool | Drug or device trial | `false` |
| `genetic` | bool | Involves genetic data | `false` |
| `multicenter` | bool | Multi-center study | `false` |
| `funding` | string | SF002 item 6 / SF094 經費來源 — the option text to check (default `不需補助`; e.g. `院內研究`) | `"不需補助"` |
| `sponsor` | string | SF094 試驗委託者 (default `無`) | `"無"` |
| `questionnaire` | bool | Uses questionnaires (SF001 item 10) | `false` |
| `doc_version` / `doc_date` | string | 中文計畫摘要 footer 版本／日期 (defaults `1.0` / today) | `"1.0"`, `"2026/11/01"` |

## `pi` (required) — usually `pi = "@cv.toml#pi"`

| Field | Type | Description | Example |
|---|---|---|---|
| `name` | string | PI Chinese name | `"林協霆"` |
| `name_en` | string | PI English name | `"Hsieh-Ting Lin"` |
| `dept` | string | Department and title | `"腫瘤內科部／醫師"` |
| `phone` | string | Contact phone | `"0920476278（院內分機1640）"` |
| `email` | string | Contact email | `"htlin222@kfsyscc.org"` |
| `training_hours` | int | SF002 「近6年內共___小時」 (left blank if absent) | `24` |
| `conflict_of_interest` | bool | `true` leaves SF094's disclosure for hand-filling instead of checking 「無任何需揭露」 | `false` |

## `co_pi` (optional, list) — usually `co_pi = "@cv.toml#co_pi"`

Each `[[co_pi]]` entry in `cv.toml`:

| Field | Type | Description |
|---|---|---|
| `name` | string | Co-PI Chinese name |
| `name_en` | string | Co-PI English name |
| `dept` | string | Department and title |
| `phone`, `email`, `training_hours`, `conflict_of_interest` | | as for `pi` |

One SF002 row is filled per co-PI (the official row is cloned); the row is removed when
there are none. Every team member (PI, co-PIs, `staff`) gets their own SF094.

## `staff` (optional, list) — 研究人員, same fields as `co_pi`

## `contact` / `supervisor` (optional tables)

`contact` (SF002 聯絡人; default: the PI) takes `name`, `phone`, `email`.
`supervisor` (SF002 總主持人／指導老師 row, removed when absent) takes the `pi` fields plus
`role` = `總主持人` or `指導老師`.

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
| `population` | string | SF002 18(1) 受試者型態 | `"轉移性乳癌患者"` |
| `age_range` | string | SF002 18(2) 年齡範圍 | `"20-90"` |
| `waiver_criteria` | list | SF005 自評項目 answered 是 (others 否); default `[3, 4]` | `[3, 4]` |
| `waiver_reason` | string | SF005 主持人說明 (default: generated retrospective rationale) | |

### `subjects.groups` (optional, list)

Array of inline tables:

```toml
groups = [
  { name = "早期G-CSF組", n = 118 },
  { name = "非早期G-CSF組", n = 764 },
]
```

## `proposal` (optional) — usually `proposal = "@中文計畫摘要.md"`

Free text for the 中文計畫摘要, one `##` section per key. A missing section keeps the
form's placeholder. Lists render as `1. … 2. …`. Keep the whole summary within 2 pages.
Full example: `irbh init tdxd-her2low` copies one (`irb_in_hurry/examples/tdxd-her2low/中文計畫摘要.md`).

| Key | Markdown heading | Form section |
|---|---|---|
| `background` | `研究背景` | 二、研究背景 |
| `objectives` | `研究目的` | 三、研究目的 (string or list) |
| `design` | `研究設計` | 五、研究設計 (appended after the generated sentence) |
| `inclusion` / `exclusion` | `納入條件` / `排除條件` | 六、研究參與者 (string or list) |
| `variables` / `endpoints` | `資料收集項目` / `研究終點` | 七、研究方法 (retrospective) |
| `methods` | `研究方法` | 七、研究方法 (prospective / trials) |
| `statistics` | `統計分析` | 九、統計分析 |
| `adverse_events` | `副作用處理` | 八、副作用處理 |
| `data_protection` | `研究參與者資料保護措施及安全監測計畫` / `資料保護措施` | 十、資料保護 (default: from `closure.data_safety`) |
| `attachments` | `附件` / `附錄` | 十一、附錄 (string or list) |

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
| `change_description` | string | Description of changes (or `"@修正說明.md"`) |
| `affects_consent` | bool | Changes affect consent form |
| `affects_risk` | bool | Changes affect risk level |

## `continuing_review` (when phase=continuing)

| Field | Type | Description |
|---|---|---|
| `enrollment_status` | string | Current enrollment status |
| `deviations` | int | Number of protocol deviations |
| `extension_requested` | bool | Requesting study extension |
