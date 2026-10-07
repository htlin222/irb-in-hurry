示範錄影（`PROMPTS.md` Part 1–4，T-DXd HER2-low 範例研究）跑出來的送審文件。每一包都從錄影中 git 標記的版本重新產生，並通過 `make validate` 排版檢查（0 錯誤）。

| 檔案 | 來源 | 內容 |
|---|---|---|
| `01_新案送審_first-submission.zip` | tag `first-submission` | SF001、SF002、SF003、SF005、SF094、中文計畫摘要 |
| `02_複審_second-submission.zip` | tag `second-submission` | SF019 複審案申請表（逐條回覆 3 項審查意見）＋ `修正後文件_revised/`（依意見修正後的新案文件） |
| `03_結案_草稿_closure-draft.zip` | 錄影結束時的狀態（保存年限改回 7 年） | SF023、SF036、SF037、SF038 |

每包都附 DOCX 和 PDF：送審以 PDF 為準（字型已內嵌），DOCX 留著備改。

**送出前要人工處理的地方**
- 這是範例研究的資料，不是真實案件。
- PDF 在 Linux 上產生，標楷體由 AR PL UKai TW 代替，排版尺寸相同。正式送審前，最好在裝有標楷體的 Windows 或 Mac 上執行一次 `make all`。
- SF019 的「原審查類別」「原審查日期」還是空白，要手動填。
- 結案包是**草稿**：SF038 的研究結果、討論、結論等 8 節還是「請填寫」。範例研究沒有真實結果，AI 也拒絕編造。
