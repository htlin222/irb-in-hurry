# Onboard an Institution (Claude procedure)

Use this when the user's committee **is not** an existing `institutions/<id>/`.
Signs: they mention another hospital or university, upload or point to their own
blank forms, or ask to "use this for my IRB". Human-facing version:
`docs/ONBOARDING.md`. Method and invariants: `docs/METHODOLOGY.md`.

## 0. Pick an id

Use a short lowercase slug of the institution (`ntuh`, `cgmh-lk`, `vghtpe`). Confirm it
with the user once.

## 1. Get the blanks into `templates/<id>/`

- If the user gives files or a folder, copy them there unchanged.
- If the user gives a forms webpage, set `templates.index_url` (+ `index_range` if paged)
  in the profile after step 2 and run `make templates`. Google Drive links are handled.
- If a form exists only as PDF or scan, note it. It will need a rebuild generator (step 6).

## 2. Scaffold and read

```bash
make onboard INST=<id>
```

Then **read `institutions/<id>/form_inventory.md` in full** before editing anything.
For each form, note:
- which labels are study data and which are committee-only or signature fields
- which checkboxes depend on config (review type, consent, study type, drug/device,
  vulnerable population, multicenter, genetic) and which are manual
- which form is the **submission checklist** (送審資料表 / 檢核表). It defines routing.

## 3. Profile: resolve every TODO

Fill `name`, `committee`, `name_en`, `submission.email`, `submission.paper` and
`font.aliases`. Ask the user for anything the blanks don't show (usually the email
and the paper-copy rule). Don't guess an email address.

Font aliases to use: 標楷體 → `[DFKai-SB, BiauKai]`, 新細明體 → `[PMingLiU]`,
細明體 → `[MingLiU]`, 微軟正黑體 → `[Microsoft JhengHei]`.

## 4. forms.py: map labels and checkboxes

- Map each label to an existing config path first (see `config-schema.md`). Common
  ones: `{study.irb_no}`, `{study.title_zh}`, `{study.title_en}`, `{pi.name}`,
  `{pi.dept}`, `{pi.phone}`, `{pi.email}`, `{subjects.planned_n}`,
  `{dates.study_start}`, `{dates.study_end}`, `{co_pi.0.name}`.
- If a label needs data that isn't in the config, **add a field** under the matching
  section, document it in `config-schema.md`, and ask the user for the value.
  Never put study facts in `forms.py`.
- Each checkbox gets a predicate on `c` (the config). Leave a box unmapped
  when it is the committee's own decision.
- Delete TODO lines for committee-only fields. Don't fill them.

## 5. Route

Translate the submission checklist into `PHASE_FORMS` using the generic
phase names. Show the user the resulting table (phase → base forms → conditional forms)
and **get confirmation**. Routing is the one place where a wrong guess means a
missing form at submission.

## 6. Forms that can't be filled

Rebuild a form instead of filling it when it has text boxes or frames, content
controls, legacy form fields, a scanned or PDF-only original, or mostly generated
prose. Write `institutions/<id>/generators.py` with `init_doc()` and
`add_header()`, and the other `scripts.docx_utils` helpers. Read `institution()`
for every name or label, and never hardcode them. Register it with its full module path.

## 7. Run and verify

```bash
# config.yml → institution: <id>
make templates && make all
```

- Fix every `⚠ <form>: labels not found in blank` line.
- `make validate` must show **0 errors**. Explain warnings to the user.
- **Look at** `output/preview/compare/*.png` (blank on the left, generated on the right) for each form,
  and report anything misplaced.
- Run `make test`.

## 8. Hand-off

Tell the user which forms are fully automatic, which have manual fields left
(signatures, committee sections), and which config fields were added. Their
`checklist.md` now lists their own submission address.

## Don'ts

- Don't edit the blanks in `templates/<id>/`. They are the gate's ground truth.
- Don't copy KFSYSCC routing or form ids to another institution.
- Don't touch `institutions/kfsyscc/` or `scripts/generators/` while onboarding someone
  else. They are the reference pack.
