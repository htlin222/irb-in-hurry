# Agentic Workflow for Clinicians — 60 分鐘示範腳本

一行一個 prompt，依序貼進對話。Prompt 只是引子，重點在看 agent 怎麼做。

## Part 0 · 概念（~20 分）

用三句話向醫師解釋：agentic AI 跟一般 ChatGPT 聊天差在哪？
你現在有哪些工具？用 BREW（Bash / Read / Edit / Write）分類給我看。
用 Bash 看看這個資料夾裡有什麼。
Read 一下 CLAUDE.md，這是什麼專案？
你現在跑在哪個 environment？我的電腦看得到你改的檔案嗎？
為什麼 plain text（.md、.toml）比 Word 更適合給 AI 和 GitHub？
用病歷來比喻 git：commit、diff、branch、push 各是什麼？
給我看最近 5 個 commit，挑一個解釋改了什麼。
用臨床例子解釋 SSOT（Single Source of Truth）。
DRY 是什麼？在這個 repo 找一個例子。
什麼是 deterministic？為什麼「AI 寫程式、程式填表」比「AI 直接填表」可靠？
奧坎剃刀跟寫 prompt 有什麼關係？

## Part 1 · 認識專案（~10 分）

畫一張圖：從 config.toml 到 IRB 送審 PDF 經過哪些步驟。
打開 config.toml，哪些欄位是醫師要自己填的？
"@cv.toml#pi" 這種寫法是什麼意思？為什麼這樣設計？

## Part 2 · 實際操作（~20 分）

先開一個 branch 叫 demo，等下的修改都在這裡做。
用 gcsf-retrospective 範例初始化，然後 make check。
跑 make all，產出了哪些表單？
把其中一張表的預覽圖給我看。
預計收案數改成 200，重跑，證明所有表單都同步更新。
用 git diff 給我看剛剛改了什麼。
故意把 review_type 改成 "fast"，跑 make check 看會怎樣。
還原剛剛的錯誤。
研究結束了，產出結案需要的表單，但不要改到 config.toml。
扮演 IRB 審查委員，用 make review 挑我的毛病。
跑 make test，這些測試在保護什麼？
把這次修改 commit，訊息用中文。

## Part 3 · 收尾（~10 分）

/irb 我想做回溯性研究：免疫治療後甲狀腺低下與存活的關係，先幫我 brainstorm。
回顧今天：哪些步驟是 AI 判斷，哪些是 deterministic 的程式？
如果我要在自己的醫院複製這套流程，第一步該做什麼？
