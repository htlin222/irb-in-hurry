# Changelog

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
