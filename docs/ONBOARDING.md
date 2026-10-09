# Onboarding your institution (fork guide)

You have your committee's blank Word forms. This guide gets you from those
files to `irbh all` producing a filled, gate-checked packet. Budget about an
hour for a 5–10 form pack. Most of that time goes on deciding routing, not
on code.

> Using Claude Code? Say *"onboard my institution's forms in templates/myhosp"*.
> The skill follows [onboard-institution.md](../.claude/skills/irb/references/onboard-institution.md)
> and does steps 2–6 with you.

## 1. Drop in the blanks

```bash
mkdir -p templates/myhosp
cp ~/Downloads/IRB-forms/*.docx templates/myhosp/      # .doc works too (needs LibreOffice)
```

Keep the original filenames. If every filename carries a code (`IRB-F01`,
`SF002`, `表單3`), it becomes the form id. Otherwise forms are numbered
`F01`, `F02`, and so on.

## 2. Scaffold

```bash
irbh onboard myhosp
```

This writes three drafts to `institutions/myhosp/` in your study folder. A local
pack there wins over an installed or bundled one with the same id
(`irbh institutions` shows which one is active):

| File | What to do with it |
|---|---|
| `form_inventory.md` | Read it first. It lists each form's paper, margins and font, then every table label, `label：＿＿` line and □ option it found. |
| `profile.toml` | Fix every `TODO`: hospital and committee name, submission email, font aliases, `lang`. |
| `forms.py` | One `blank_generator(...)` per form. Recognised labels are pre-mapped (`計畫名稱 → {study.title_zh}`), and the rest are `# TODO` lines. |

Re-running never overwrites your edits unless you pass `--force`
(`irbh onboard myhosp --force`).

## 3. Finish the label map

For each `# TODO` in `forms.py`:

```python
generate_f002 = blank_generator("F002", fields={
    "計畫名稱": "{study.title_zh}",                       # format string over config.toml
    "執行期間": "{dates.study_start} 至 {dates.study_end}",
    "受試者人數": lambda c: f"{c['subjects']['planned_n']} 人",   # or any callable
    # "審查委員意見": "",                                 # leave committee-only fields out
}, checks={
    "簡易審查": lambda c: c["study"]["review_type"] == "expedited",
    "需取得知情同意": lambda c: not c["subjects"]["consent_waiver"],
})
```

Rules of thumb:

- **Values go next to labels.** A table label fills the next distinct cell to the
  right, or the cell below if the label is last in its row. A paragraph label fills its
  `＿＿＿` run, or gets `：value` appended.
- **The key must match the label as printed.** Spaces and colons are ignored. If
  the blank says `計畫主持人（簽名）`, use that full text as the key.
- **Need a value that isn't in `config.toml` yet?** Add it under the matching
  section (`study`, `pi`, `subjects`, …) and document it in
  `.claude/skills/irb/references/config-schema.md`. Never hardcode it in `forms.py`.
- **Checkbox keys are the option text right after the □.**
- Fields for the committee, signatures and dates signed by hand: leave them out.

## 4. Route forms to phases

Open your committee's own *submission checklist* form (送審資料表). It is the
routing spec. Translate it into `PHASE_FORMS`:

```python
PHASE_FORMS = {
    "new": {
        "base": ["F01", "F02", "F09"],
        "conditions": [
            (lambda c: c["study"]["review_type"] == "expedited", ["F03"]),
            (lambda c: c["subjects"]["consent_waiver"], ["F05"]),
            (lambda c: not c["subjects"]["consent_waiver"], ["F06"]),
        ],
    },
    "closure": {"base": ["F20", "F21"], "conditions": []},
}
```

Use the generic phase names (`new`, `amendment`, `re_review`, `continuing`,
`closure`, `sae`, `ib_update`, `import`, `suspension`, `appeal`) where they fit,
so the Makefile shortcuts, dashboard and skill keep working. Add your own
names freely for anything else.

## 5. Switch on and run

```toml
# config.toml (top-level, before the first [table])
institution = "myhosp"
```

```bash
irbh templates   # indexes your blanks → templates/myhosp/index.json
irbh all         # generate → PDF → layout gate → dashboard
```

The generator prints `⚠ F02: labels not found in blank: …` for any key that
didn't match. Fix the key, or remove it.

## 6. Pass the gate

`irbh validate` must report **0 errors**. Then open
`output/preview/compare/*.png`, which shows the official blank on the left and the generated form on the right.

| Gate message | Usual fix |
|---|---|
| 中文字型為「X」而非 … | `font.name` in the profile doesn't match the blank's real font, or a rebuilt form isn't using `init_doc` |
| 紙張大小 / 邊界 … | a rebuilt form: add its margins to `page.per_form_margins` |
| 字元超出 Big5 | replace simplified or rare characters, or set `font.encoding: null` if your font covers them |
| 頁數 > 官方空白表單 | long answers: shorten them, or allow it with `templates.max_pages: {F02: 3}` |

## 7. (Optional) Rebuild forms that can't be filled

Text boxes, content controls, PDF-only forms and generated prose (a protocol summary)
need a python-docx generator. Copy the shape of
`irb_in_hurry/generators/proposal.py` into `institutions/myhosp/generators.py` and
register it with its full module path:

```python
"F07": ("中文計畫摘要", "institutions.myhosp.generators", "generate_summary"),
```

Use `init_doc()`, `add_header()`, `add_p()`, `add_ct()` and `check()` from
`irb_in_hurry.docx_utils`. They read the profile, so `institution().heading`,
`institution().irb_no_label`, the font and the page setup all follow your institution.

## 8. Share it (optional)

An `institutions/<id>/` folder is self-contained. Two ways to pass it on:

- **PR it into irb-in-hurry** as `irb_in_hurry/institutions/<id>/` (change the
  module paths to `irb_in_hurry.institutions.<id>.forms` and add it to the
  `irb_in_hurry.institutions` entry points in `pyproject.toml`). It then ships
  with every install.
- **Publish it as its own small package**, so colleagues `uv tool install
  irb-in-hurry --with irb-pack-myhosp`. Rename the folder to an importable
  package (`irb_pack_myhosp/`), point `forms_module` and the `FORM_REGISTRY`
  module paths at `irb_pack_myhosp.forms`, and register it:

  ```toml
  # pyproject.toml of irb-pack-myhosp
  [project]
  name = "irb-pack-myhosp"
  dependencies = ["irb-in-hurry>=2"]

  [project.entry-points."irb_in_hurry.institutions"]
  myhosp = "irb_pack_myhosp"   # the package folder holding profile.toml + forms.py
  ```

  Ship `profile.toml` inside the package (hatchling includes it by default).

Either way, don't commit or package the blanks themselves (`templates/` is
gitignored; they are the institution's documents), and don't commit real study data.
