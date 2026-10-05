# Distill: Raw Text → config.toml

## Overview

When a user provides free-form text (proposal, study idea, email, abstract, or even a casual description), Claude should **distill** it into the study's source files — no manual TOML editing needed:

| File | Holds |
|------|-------|
| `config.toml` | Structured metadata: `phase`, `[study]`, `[dates]`, `[subjects]`, and `pi`/`co_pi`/`proposal` as `@` references |
| `cv.toml` | People: `[pi]` and `[[co_pi]]` (name, name_en, dept, phone, email) |
| `中文計畫摘要.md` | Proposal prose: one `## 標題` per section (研究背景、研究目的、研究設計、納入條件、排除條件、資料收集項目、研究終點、研究方法、統計分析、附件) |

Put long prose in Markdown, never in TOML strings. A section made only of `-` / `1.` items becomes a list; anything else becomes paragraphs.

## Workflow

1. **Save raw input** to `raw/` with a descriptive filename (e.g., `raw/proposal_20260330.md`)
2. **Extract structured fields** into `config.toml`, people into `cv.toml`, and proposal prose into `中文計畫摘要.md` (to start from a template instead, `make init EXAMPLE=tdxd-her2low` copies an example from `examples/`)
3. **Run `make check`** to resolve `@` references and validate required fields
4. **Ask user to confirm** any uncertain fields before generating forms
5. **Proceed** with `make all` + `make review`

## Extraction Rules

Read the user's text and map to config fields (dotted names below are TOML tables; `pi.*`/`co_pi` live in `cv.toml`). Use these heuristics:

### Study Identification
| Look for | Maps to |
|----------|---------|
| IRB number, case number, 編號 | `study.irb_no` |
| Chinese title, 計畫名稱 | `study.title_zh` |
| English title | `study.title_en` |
| If no English title given | Generate one from Chinese title |

### Study Classification
| Keywords | `study.type` | `study.review_type` |
|----------|-------------|-------------------|
| 回溯, retrospective, chart review, 病歷審查 | `retrospective` | `expedited` |
| 前瞻, prospective, observational, 觀察 | `prospective` | `expedited` or `full_board` |
| 臨床試驗, clinical trial, RCT, randomized | `clinical_trial` | `full_board` |
| 基因, genetic, genomic, NGS, sequencing | `genetic` | `full_board` |
| 多中心, multicenter, multi-site | set `multicenter = true` | varies |

### Study Design
| Keywords | `study.design` |
|----------|---------------|
| 世代, cohort | `cohort` |
| 病例對照, case-control | `case_control` |
| 橫斷面, cross-sectional | `cross_sectional` |
| 隨機, randomized, RCT | `rct` |
| 單臂, single-arm | `single_arm` |

### Auto-set Rules
- `retrospective` → `consent_waiver = true`, `review_type = "expedited"`
- `clinical_trial` + drug keywords → `drug_device = true`
- `genetic` keywords → `genetic = true`
- If no phase mentioned → default `phase = "new"`

### PI Information
| Look for | Maps to |
|----------|---------|
| 主持人, PI, investigator + Chinese name | `pi.name` |
| English name after Chinese name | `pi.name_en` |
| 科, 部, department | `pi.dept` |
| phone, 電話, 分機 | `pi.phone` |
| email, @kfsyscc.org | `pi.email` |
| 共同主持人, co-PI, co-investigator | `[[co_pi]]` |

### Dates
| Look for | Maps to |
|----------|---------|
| 起始, start date, 開始 | `dates.study_start` |
| 結束, end date, 截止 | `dates.study_end` |
| 資料期間, data period, 病歷期間 | `dates.data_period` |
| Format: convert to "YYYY年MM月DD日" | |

### Subjects
| Look for | Maps to |
|----------|---------|
| 人數, sample size, N=, n=, 收案, enrollment | `subjects.planned_n` |
| 組, group, arm | `subjects.groups` |
| 脆弱, vulnerable, 兒童, children, 囚犯 | `subjects.vulnerable_population = true` |

### Proposal Prose (→ `中文計畫摘要.md`)
| Look for | `## 標題` |
|----------|-----------|
| 背景, rationale, background | `## 研究背景` |
| 目的, aim, objective, hypothesis | `## 研究目的` |
| 設計, design, 分組方式 | `## 研究設計` |
| 納入, inclusion | `## 納入條件` |
| 排除, exclusion | `## 排除條件` |
| 收集變項, variables, data items | `## 資料收集項目` |
| 終點, endpoint, outcome | `## 研究終點` |
| 方法, procedures (prospective / trial) | `## 研究方法` |
| 統計, statistics, sample size calculation | `## 統計分析` |

### Phase (if not new case)
| Keywords | `phase` |
|----------|---------|
| 修正, amendment, 變更 | `amendment` |
| 期中, continuing, annual review | `continuing` |
| 結案, closure, 結案報告 | `closure` |
| 不良反應, SAE, adverse event | `sae` |
| Default (no keywords) | `new` |

Keep `phase = "new"` as the default in `config.toml`; for a later phase, run `make <phase>` (e.g. `make closure` = `make all PHASE=closure`) instead of editing the file.

## What to Do When Information is Missing

For **required fields** that can't be extracted:
- `study.irb_no` → Ask user: "IRB 編號是什麼？（如果是新案尚未取得，可先留空）"
- `pi.name` → Ask user: "計畫主持人姓名？"
- `dates.study_start/end` → Ask user: "預計研究期間？"

For **optional fields** with sensible defaults:
- `study.project_no` → "不適用"
- `closure.data_safety.*` → `deidentified = true`, `encrypted = true`, `retention_years = 7`
- `subjects.vulnerable_population` → `false`

## Example

**User input:**
> 我想做一個回溯性研究，看2018到2023年間在我們醫院接受免疫治療的肺癌病人，大約200人，看甲狀腺功能有沒有受影響。我是腫瘤內科的陳雅文醫師。

**Distilled `config.toml`:**
```toml
phase = "new"

pi       = "@cv.toml#pi"
co_pi    = "@cv.toml#co_pi"
proposal = "@中文計畫摘要.md"

[study]
irb_no      = ""   # ask user
title_zh    = ""   # generate from description
title_en    = ""   # generate from description
type        = "retrospective"
design      = "cohort"
review_type = "expedited"
drug_device = false
genetic     = false
multicenter = false

[dates]
data_period = "2018年01月01日 至 2023年12月31日"

[subjects]
planned_n      = 200
consent_waiver = true
```

**Distilled `cv.toml`:**
```toml
co_pi = []   # no co-PI mentioned; replace with [[co_pi]] tables when there are some

[pi]
name = "陳雅文"
dept = "腫瘤內科部／醫師"
```

**Distilled `中文計畫摘要.md`:**
```markdown
## 研究目的

- 主要目的：分析接受免疫治療之肺癌患者甲狀腺功能異常之發生率。

## 納入條件

- 2018年01月01日至2023年12月31日間於本院接受免疫治療之肺癌患者。

## 資料收集項目

年齡、性別、免疫治療藥物種類、甲狀腺功能檢驗值（TSH、Free T4）及發生時間。
```

Then Claude should:
1. Generate a proper Chinese + English title from the description
2. Ask for IRB number and study period dates
3. Fill remaining fields with defaults
4. Write `config.toml`, `cv.toml`, `中文計畫摘要.md`, run `make check`, then `make all`
