# 示範錄影：PROMPTS.md Part 1–4

`PROMPTS.md` Part 1–4 的 21 個 prompt，一字不改送進 Claude Code，一個 prompt 一章，
用 [stagecast](https://github.com/htlin222/stagecast) 錄成可以逐章播放的網頁。
`site/` 由 `.github/workflows/pages.yml` 發佈到 GitHub Pages。

## 檔案

| | |
|---|---|
| `stagecast.toml` | 21 章：每章的 prompt 與完成檢查 |
| `prompts/NN.md` | 送出的原文（取自 PROMPTS.md） |
| `agent.sh` | 啟動 Claude Code；第 2 章起 `--continue`，21 章是同一段對話 |
| `turn_ended.py` + `hook-settings.json` | Stop hook：記錄「收到第 N 題的那一輪已結束」 |
| `check` | 每章的檢查：`answered`（該輪結束）、`edited`（計畫檔真的改了） |
| `responder.sh` | AI 用選擇題反問時，代替醫師作答（只選與本研究事實相符的選項） |
| `template.html` | 播放頁樣板（stagecast 上游缺此檔，放到 `stagecast/site/`） |
| `site/` | 建置結果：`index.html`、`prompts.json`、`casts/` |

## 完成訊號

問答型的章節沒有產物可檢查，所以完成訊號是「收到這一題的那一輪已經結束」（Stop hook）。
有產物的章節再加上產物本身：分支不是 `main`、`planned_n = 220` 且有 PDF、
git 裡有「第一次送審」、計畫檔內容真的改變、`retention_years` 為 10 再回到 7、
`SF019`、`SF036` 確實產出。

第 8 章 AI 會停下來問「220 人的依據是哪一種」——檔案裡沒有記錄，它拒絕自己編。
現場示範時由醫師回答；錄影時由 `responder.sh` 選「全數納入」。

## 重錄

```sh
git clone https://github.com/htlin222/stagecast ../stagecast
cp template.html ../stagecast/site/template.html
git clone -b main https://github.com/htlin222/irb-in-hurry irb-in-hurry
git -C irb-in-hurry remote remove origin        # 錄影中的 commit/tag 不會推出去
(cd irb-in-hurry && uv sync && make templates)
./responder.sh & ../stagecast/stagecast record; kill %1
../stagecast/stagecast build
```

需要 `tmux`、`asciinema`、`uv`、`claude`，以及 LibreOffice（PDF）。
第一次啟動 Claude Code 時要先手動完成主題、信任資料夾、bypass permissions 三個確認。
