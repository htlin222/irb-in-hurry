# Changelog

## Unreleased — fill the official KFSYSCC blanks

- **KFSYSCC new-case forms fill the official blanks** (htlin222/irb-in-hurry#15,
  htlin222/irb-in-hurry#16): SF001, SF002 (v12), SF003, SF004, SF005, SF022, SF094 and
  中文計畫摘要 are copied from `templates/kfsyscc/` and filled in place
  (`institutions/kfsyscc/fill.py`), keeping the official header (版次/編修日期/文件標號),
  every option, instructions and reviewer sections. SF002 drops the 總主持人, 研究人員
  and 附表 parts a study doesn't need and clones a row per co-PI; SF094 is produced once
  per team member with the name on its own line (htlin222/irb-in-hurry#19); 中文計畫摘要 follows the
  official 11 headings with a 版本／日期／第 X 頁共 Y 頁 footer. Without a cached
  blank the old rebuild is used, with a warning.
- **`template_fill.Form`**: scoped `check` / `put` / `cell` / `sub`, row clone/delete,
  block delete and paragraph insertion for any pack; inserted values are runs of
  their own in the form font.
- **Wingdings checkboxes** (`w:sym` and private-use characters) become □/■/√ in the
  form font, so PDFs no longer show ☒ for unchecked boxes (htlin222/irb-in-hurry#18); Symbol-font ≤/≥
  become ≦/≧; CJK compatibility ideographs from .doc conversion are NFC-normalized.
- **Layout gate**: official-text coverage < 50% is now an error (a rebuild is not the
  official form) and a 版次/編修日期 that differs from the cached blank is an error
  (non-current form). Fonts used by the blank itself are accepted. The Big5 check
  suggests replacements (≥→≧, ✓→√, …) and ignores whitespace (htlin222/irb-in-hurry#15, htlin222/irb-in-hurry#19).
- **`irbh templates`**: records each blank's 版次/編修日期 in `index.json`; `--update`
  re-downloads and lists revised forms; when the index site is unreachable the blanks
  already in `templates/<id>/` are indexed.
- **Linux rendering** (htlin222/irb-in-hurry#17): `fonts.conf` maps 新細明體/細明體/PMingLiU/MingLiU/MS Mincho
  → AR PL UMing TW and 微軟正黑體/Noto CJK JP → Noto CJK TC, and prefers zh-TW glyphs;
  LibreOffice runs in `zh_TW.UTF-8` when that locale is installed.
- New optional config fields (see `config-schema.md`): `staff`, `contact`,
  `supervisor`, `pi.training_hours`, `study.funding` / `sponsor` / `doc_version` /
  `doc_date`, `subjects.population` / `age_range` / `waiver_criteria` /
  `waiver_reason`, and proposal sections `adverse_events` / `data_protection`.

## 2.0.0 — installable package

IRB-in-Hurry is now a Python package (`irb-in-hurry`) with one command, `irbh`.
Each study lives in its own folder; the engine is installed once and upgraded
with `uv tool upgrade irb-in-hurry`.

- **`irbh` CLI**: `init`, `check`, `generate`, `pdf`, `templates`, `onboard`,
  `validate`, `all`, `dashboard`, `review`, `set-phase`, `institutions`,
  `skill`, `doctor`; `irbh <phase>` = `irbh all --phase <phase>`; `-C DIR`.
  The Makefile is now a thin wrapper over it.
- **Study folder = current directory**: `config.toml`, `templates/<id>/`,
  `output/` and local packs are resolved from the cwd, not from the code's
  location. `$IRB_TEMPLATES` shares one blank-form cache between studies.
- **Institution packs** are found in `institutions/<id>/` of the study folder
  (what `irbh onboard` writes), then in installed packages registered under the
  `irb_in_hurry.institutions` entry point, then among the bundled packs.
- **Bundled**: the KFSYSCC pack, the example studies and the Claude Code skill
  ship inside the wheel; `irbh init` copies an example and the skill into a
  new study folder.
- `dashboard.sh` is replaced by `irbh dashboard` (no bash needed).
- MIT `LICENSE` file added; CI also smoke-tests the built wheel outside the repo;
  tagging `vX.Y.Z` builds a GitHub Release (and publishes to PyPI once enabled).

### Migrating from 1.x

- Code moved from `scripts/` to `irb_in_hurry/`, and `institutions/` and
  `examples/` moved under it. Replace `from scripts.…` with
  `from irb_in_hurry.…` in your own pack's `forms.py` (e.g.
  `from irb_in_hurry.template_fill import blank_generator`).
- `uv run python scripts/<x>.py` → `irbh <x>` (or `uv run irbh <x>` in a checkout).
- A pack you onboarded into the repo's `institutions/<id>/` keeps working when it
  sits in the study folder's `institutions/<id>/`; its `forms_module`
  (`institutions.<id>.forms`) is unchanged.
