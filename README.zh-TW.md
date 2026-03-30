# IRB-in-Hurry

[和信治癌中心醫院](https://www.kfsyscc.org/) IRB（人體試驗委員會）送審文件自動化產生工具。

填入 YAML 設定檔中的研究資料，執行一行指令，即可產生所有必要的 IRB 送審表單 Word 文件 — 簽名後即可送出。

[English README](README.md)

## 功能特色

- **涵蓋 11 類 IRB 審查**：新案、修正案、複審、期中、結案、嚴重不良反應、主持人手冊、專案進口、其他、暫停/終止、申覆
- **44+ 表單登錄**：依研究類型與送審階段自動選取所需表單
- **智慧判斷**：回溯性研究自動選取簡易審查 + 免取得知情同意相關表單
- **DOCX 產生**：使用 python-docx，標楷體字型、■/□ 勾選格式
- **PDF + PNG 預覽**：轉檔後可視覺化驗證排版
- **純文字清單**：■/□ 追蹤自動產生表單與手動步驟
- **彩色儀表板**：一目了然的送審進度
- **Claude Code 技能**：AI 輔助表單準備

## 快速開始

```bash
# 1. 複製並安裝
git clone https://github.com/htlin222/irb-in-hurry.git
cd irb-in-hurry
make setup

# 2. 編輯 config.yml 填入研究資料
#    （或複製範例設定）
cp tests/fixtures/sample_retrospective.yml config.yml

# 3. 一鍵產生所有文件
make all
```

## 使用方式

### Makefile 指令

| 指令 | 說明 |
|------|------|
| `make all` | 產生 DOCX + PDF + 儀表板 |
| `make generate` | 僅產生 DOCX 表單 |
| `make pdf` | 轉換為 PDF + PNG 預覽 |
| `make dashboard` | 顯示送審狀態 |
| `make checklist` | 檢視 ■/□ 清單 |
| `make test` | 執行測試 |
| `make clean` | 清除產生的檔案 |
| `make new` | 切換至新案審查 + 產生 |
| `make closure` | 切換至結案審查 + 產生 |
| `make amendment` | 切換至修正案審查 + 產生 |
| `make continuing` | 切換至期中審查 + 產生 |

### 工作流程

```
config.yml → generate_all.py → output/*.docx → convert.py → output/*.pdf
                                                           → output/preview/*.png
                                  checklist.md ← checklist.py
```

1. **編輯 `config.yml`** — 填入研究基本資料（IRB 編號、計畫名稱、主持人、日期、研究類型）
2. **`make all`** — 產生 DOCX、轉換 PDF、顯示儀表板
3. **檢查預覽** — 確認 `output/preview/*.png` 排版正確
4. **完成手動步驟** — 簽名、附上計畫書、email 至 irb@kfsyscc.org

### 設定檔結構

```yaml
study:
  irb_no: "20250801A"           # IRB 編號
  title_zh: "研究中文標題"        # 中文計畫名稱
  title_en: "English Title"     # 英文計畫名稱
  type: retrospective           # retrospective|prospective|clinical_trial
  review_type: expedited        # exempt|expedited|full_board

pi:
  name: "林協霆"                 # 計畫主持人
  dept: "腫瘤內科部／醫師"        # 單位／職稱
  email: "htlin222@kfsyscc.org"

subjects:
  planned_n: 300                # 預計收錄人數
  consent_waiver: true          # 回溯性研究自動設為 true

phase: new                     # new|amendment|continuing|closure|sae|...
```

### 研究類型 → 表單選取

| 研究類型 | 審查方式 | 自動選取表單 |
|---------|---------|-----------|
| 回溯性病歷審查 | 簡易審查 | SF001、SF002、SF094、SF003、SF005 |
| 前瞻性觀察研究 | 簡易/一般審查 | SF001、SF002、SF094、SF062 |
| 臨床試驗（藥品） | 一般審查 | SF001、SF002、SF094、SF063、SF090、SF022 |
| 基因研究 | 一般審查 | SF001、SF002、SF094、SF075 |

## 系統需求

- Python 3.10+
- [python-docx](https://python-docx.readthedocs.io/) — DOCX 產生
- [PyYAML](https://pyyaml.org/) — 設定檔解析
- [LibreOffice](https://www.libreoffice.org/) — DOCX→PDF 轉換（`brew install --cask libreoffice`）
- [poppler](https://poppler.freedesktop.org/) — PDF→PNG 預覽（`brew install poppler`）

## 表單對照表

| 送審階段 | 表單代號 | 表單名稱 |
|---------|---------|---------|
| 新案審查 | SF001 | 新案審查送審資料表 |
| | SF002 | 研究計畫申請書 |
| | SF094 | 顯著財務利益申報表 |
| | SF003 | 簡易審查範圍檢核表 |
| | SF005 | 免取得知情同意檢核表 |
| 結案審查 | SF036 | 結案審查送審資料表 |
| | SF037 | 結案報告摘要表 |
| | SF038 | 結案報告書 |
| | SF023 | 資料及安全性監測計畫報告書 |
| 修正案審查 | SF014 | 修正案審查送審資料表 |
| | SF015 | 修正案申請表 |
| | SF016 | 修正前後對照表 |
| 期中審查 | SF030 | 期中審查送審資料表 |
| | SF031 | 期中報告書 |
| | SF032 | 計畫展延申請表 |

## 授權條款

MIT
