<p align="center">
  <img src="docs/assets/banner.svg" alt="IRB-in-Hurry — 和信治癌中心醫院 IRB 送審表單自動產生工具：幾個純文字檔、一行指令、43 份表單" width="100%">
</p>

# IRB-in-Hurry：和信醫院 IRB 送審表單自動產生器

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-pytest-brightgreen.svg)](#測試)
[![Forms](https://img.shields.io/badge/IRB%20forms-43%2F43-brightgreen.svg)](#表單涵蓋範圍)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](#授權條款)

[和信治癌中心醫院](https://www.kfsyscc.org/) IRB（人體試驗委員會）送審文件自動化產生工具。

用純文字寫下研究資料（`config.toml` 放結構化資料、`cv.toml` 放研究團隊、`中文計畫摘要.md` 放計畫內容），執行一行指令，即可產生所有必要的 IRB 送審表單 Word 文件 — 簽名後即可送出。

[English README](README.md)

---

## 為什麼要做這個

人體試驗委員會（IRB）是醫學研究史上最重要的發明之一。它誕生於紐倫堡審判（1947年）的灰燼之中，經由赫爾辛基宣言（1964年）與貝爾蒙特報告（1979年）確立制度化。IRB 的存在，是為了確保沒有任何人在未經知情同意、適當風險評估與倫理監督的情況下被納入研究。這些是不可妥協的原則。塔斯基吉事件、731 部隊，以及無數醫學實驗的黑暗歷史，都在提醒我們為什麼需要它。

**但在某個時間點，官僚體制吞噬了初衷。**

原本是為了保護受試者的制度，已經僵化成一場文書馬拉松。光是在[和信治癌中心醫院](https://www.kfsyscc.org/human/common_files/1)，研究者就必須面對 **11 類送審類別**、**43 種以上的表單** — 每一份都有自己的版本號、格式要求和勾選慣例。一個單純的回溯性病歷審查（最低風險、不接觸病人、去識別化資料）需要填 5 份表單。臨床試驗？加倍。修正計畫書裡的一個錯字？再來 4 份。

研究者的時間是有限的。每一個花在把 IRB 編號複製貼上到 SF037 表頭的小時，就是一個沒有用來分析資料、撰寫論文、或 — 最重要的 — 照顧病人的小時。表單本身不是問題。問題是填寫它們是一種**無意義的、重複的、容易出錯的勞動**，而這種勞動應該由機器來做。

這個專案不會繞過 IRB。不會跳過倫理審查。不會自動核准任何東西。它只是用你提供的資料，填好 IRB 要求的表單，讓你可以專注在真正需要人類判斷力的部分：研究設計、風險評估，以及保護你的受試者。

> 「研究倫理在於設計，不在於文書。」

**IRB-in-Hurry：因為你的時間應該花在科學上。**

---

## 功能特色

- **涵蓋 11 類 IRB 審查**：新案、修正案、複審、期中、結案、嚴重不良反應、主持人手冊、專案進口、其他、暫停/終止、申覆
- **43 個表單產生器**：依研究類型與送審階段自動選取所需表單
- **智慧判斷**：回溯性研究自動選取簡易審查 + 免取得知情同意相關表單
- **DOCX 產生**：使用 python-docx，標楷體字型、■/□ 勾選格式
- **PDF + PNG 預覽**：轉檔後可視覺化驗證排版
- **純文字清單**：■/□ 追蹤自動產生表單與手動步驟
- **致委員會函稿**：每個送審階段附一封禮貌、恭敬、明確的送審信草稿，事實取自 `config.toml`，需本人撰寫處以【請填寫】標示
- **彩色儀表板**：一目了然的送審進度
- **Claude Code 技能**：AI 輔助表單準備

## 表單涵蓋範圍

所有表單皆依據 [和信治癌中心醫院 IRB 網站](https://www.kfsyscc.org/human/common_files/1)實作：

| 類別 | 名稱 | 表單 | 狀態 |
|------|------|------|------|
| 新案 | [新案審查](https://www.kfsyscc.org/human/common_files/1) | SF001, SF002, SF094, SF003-005 | ■ 完成 |
| 複審 | [複審案審查](https://www.kfsyscc.org/human/common_files/2) | SF019 | ■ 完成 |
| 修正 | [修正案審查](https://www.kfsyscc.org/human/common_files/3) | SF014, SF015, SF016 | ■ 完成 |
| 期中 | [期中審查](https://www.kfsyscc.org/human/common_files/4) | SF030, SF031, SF032 | ■ 完成 |
| 結案 | [結案審查](https://www.kfsyscc.org/human/common_files/5) | SF036, SF037, SF038, SF023 | ■ 完成 |
| 不良反應 | [嚴重不良反應](https://www.kfsyscc.org/human/common_files/6) | SF079, SF044, SF074, SF080, SF024 | ■ 完成 |
| 主持人手冊 | [主持人手冊](https://www.kfsyscc.org/human/common_files/7) | SF082, SF083, SF084, SF085 | ■ 完成 |
| 專案進口 | [專案進口](https://www.kfsyscc.org/human/common_files/8) | SF066, SF067, SF068, SF093 | ■ 完成 |
| 其他 | [其他表單](https://www.kfsyscc.org/human/common_files/9) | SF076 | ■ 完成 |
| 暫停 | [計畫暫停](https://www.kfsyscc.org/human/common_files/10) | SF047, SF048 | ■ 完成 |
| 申覆 | [申覆案審查](https://www.kfsyscc.org/human/common_files/11) | SF077, SF054 | ■ 完成 |
| 同意書 | — | SF062, SF063, SF075, SF090, SF091, SF092 | ■ 完成 |

## 快速開始

```bash
# 1. 複製並安裝
git clone https://github.com/htlin222/irb-in-hurry.git
cd irb-in-hurry
make setup

# 2. 從範例開始（或直接編輯 config.toml / cv.toml / 中文計畫摘要.md）
make init EXAMPLE=tdxd-her2low      # HER2 低表現 T-DXd vs 化療 PSM，含完整中文計畫摘要
#   make init EXAMPLE=gcsf-retrospective FORCE=1   # 亦可測試結案流程
make check                          # 解析 @引用、檢查必填欄位

# 3. 一鍵產生所有文件
make all
```

## 使用方式

### Makefile 指令

| 指令 | 說明 |
|------|------|
| `make all` | 產生 DOCX + PDF + 排版檢查 + 儀表板 |
| `make check` | 解析 `config.toml` 的 `@引用` 並檢查必填欄位 |
| `make init EXAMPLE=…` | 將 `examples/` 的範例研究複製到根目錄 |
| `make templates` | 下載官網官方空白表單（只需一次） |
| `make validate` | 排版／字型安全檢查（A4、標楷體、Win/Mac 通用、對照官方空白表單） |
| `make generate` | 僅產生 DOCX 表單 |
| `make pdf` | 轉換為 PDF + PNG 預覽 |
| `make dashboard` | 顯示送審狀態 |
| `make checklist` | 檢視 ■/□ 清單 |
| `make review` | 模擬 IRB 審查委員檢閱產生的表單 |
| `make test` | 執行測試 |
| `make lint` | ruff 程式碼檢查（`make format` 自動修正） |
| `make clean` | 清除產生的檔案 |
| `make closure` | 即 `make all PHASE=closure`；任何階段皆可（`new`、`amendment`、`continuing`、`sae`…），不會改寫 `config.toml` |
| `make review` | 模擬 IRB 審查委員意見 |
| `make set-phase PHASE=closure` | 將階段寫入 `config.toml`（只改 `phase =` 那一行，保留註解） |

### 工作流程

```
config.toml ─┬─ @cv.toml
             └─ @中文計畫摘要.md
     ↓
config.py → generate_all.py → output/*.docx → convert.py → output/*.pdf
                                                           → output/preview/*.png
                                  checklist.md ← checklist.py
                                  output/IRB_致委員會函稿_*.md ← cover_letter.py
output/*.docx + templates/official/ (官方空白表單) → validate_layout.py
                                                 → output/layout_report.md
                                                 → output/preview/compare/*.png
```

1. **編輯純文字來源** — `config.toml`（IRB 編號、計畫名稱、日期、研究類型）、
   `cv.toml`（主持人／共同主持人）、`中文計畫摘要.md`（背景、目的、方法…）；執行 `make check`
2. **`make all`** — 產生 DOCX、轉換 PDF、顯示儀表板
3. **排版安全檢查** — `make validate` 必須 0 錯誤；查看 `output/layout_report.md`
   與 `output/preview/compare/*.png`（左：官方空白表單，右：產生結果）
4. **以 PDF 交件** — 字型已嵌入，Windows 與 Mac 顯示一致；IRB 需修改時才附 DOCX
5. **完成手動步驟** — 簽名、附上計畫書、email 至 irb@kfsyscc.org

### 單一資料來源（SSOT）

表單所需的一切都是純文字。`config.toml` 存放結構化資料；任何寫成 `"@檔案"` 或
`"@檔案#鍵"` 的值，都會被該檔案的內容取代，讓文字與人員資料各自用最適合的格式維護：

```toml
# config.toml
phase    = "new"                 # new | amendment | continuing | closure | sae | …
pi       = "@cv.toml#pi"
co_pi    = "@cv.toml#co_pi"
proposal = "@中文計畫摘要.md"

[study]
irb_no      = ""                 # 核發前留空
title_zh    = "研究中文標題"
title_en    = "English Title"
type        = "retrospective"    # retrospective | prospective | clinical_trial | genetic
review_type = "expedited"        # exempt | expedited | full_board

[subjects]
planned_n      = 300
consent_waiver = true
```

```toml
# cv.toml — 跨研究重複使用
[pi]
name  = "林協霆"                  # 計畫主持人
dept  = "腫瘤內科部／醫師"         # 單位／職稱
email = "htlin222@kfsyscc.org"
```

```markdown
<!-- 中文計畫摘要.md — 每個 ## 標題對應官方表單的一個章節 -->
## 研究背景
荷爾蒙受體陽性乳癌……（換行會自動接合，中文之間不留空白）

## 納入條件
- 年滿20歲……
- 轉移後曾接受CDK4/6抑制劑……
```

其他長篇文字也同樣處理，例如 `change_description = "@修正說明.md"`。
完整欄位說明見 [config-schema](.claude/skills/irb/references/config-schema.md)。

### 研究類型 → 表單選取

| 研究類型 | 審查方式 | 自動選取表單 |
|---------|---------|-----------|
| 回溯性病歷審查 | 簡易審查 | SF001、SF002、SF094、SF003、SF005 |
| 前瞻性觀察研究 | 簡易/一般審查 | SF001、SF002、SF094、SF062 |
| 臨床試驗（藥品） | 一般審查 | SF001、SF002、SF094、SF063、SF090、SF022 |
| 基因研究 | 一般審查 | SF001、SF002、SF094、SF075 |

## 測試

```bash
make test
```

測試涵蓋設定檔載入與 `@引用`、表單選取邏輯、DOCX 內容驗證、清單產生，以及新案與結案的端對端產生測試。

## 系統需求

- Python 3.11+（以標準函式庫 `tomllib` 讀取 TOML）
- [python-docx](https://python-docx.readthedocs.io/) — DOCX 產生
- [LibreOffice](https://www.libreoffice.org/) — DOCX→PDF 轉換（`brew install --cask libreoffice`；Windows：`winget install TheDocumentFoundation.LibreOffice`；Linux：`apt install libreoffice-writer fonts-arphic-ukai`）
- [poppler](https://poppler.freedesktop.org/) — PDF→PNG 預覽（`brew install poppler`）

## 參考資料

- [和信治癌中心醫院 IRB 表單下載](https://www.kfsyscc.org/human/common_files/1) — 官方表單
- [紐倫堡守則（1947）](https://zh.wikipedia.org/wiki/%E7%BA%BD%E4%BC%A6%E5%A0%A1%E5%AE%88%E5%88%99) — 研究倫理基石
- [赫爾辛基宣言（1964）](https://www.wma.net/policies-post/wma-declaration-of-helsinki/) — 醫學研究倫理原則
- [貝爾蒙特報告（1979）](https://www.hhs.gov/ohrp/regulations-and-policy/belmont-report/) — 尊重、善行、正義
- [聯邦法規第 45 篇第 46 部分](https://www.hhs.gov/ohrp/regulations-and-policy/regulations/45-cfr-46/) — 美國人體試驗聯邦法規

## 授權條款

MIT
