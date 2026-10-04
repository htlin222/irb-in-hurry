# Methodology: from an institution's DOCX forms to a submission-ready packet

IRB-in-Hurry is a **method for processing a set of official Word forms**, not
just a KFSYSCC tool. Any committee that publishes blank `.docx`/`.doc` forms
(an IRB, REC, or ethics committee, or any office that runs on paperwork) fits the
same pipeline. KFSYSCC is the reference implementation, with 43 forms in `institutions/kfsyscc/`.

```
 study facts            institution knowledge                 per-submission output
┌───────────┐   ┌──────────────────────────────────────┐   ┌──────────────────────────┐
│config.yml │──▶│ forms.py   phase + study → form list │──▶│ output/*.docx            │
│ (one SSOT)│   │ generators fill / rebuild each form  │   │ output/*.pdf (fonts emb.)│
└───────────┘   │ profile.yml page · font · names      │   │ checklist.md  ■/□        │
                └──────────────────────────────────────┘   │ layout_report.md (gate)  │
                         ▲                                  └──────────────────────────┘
                templates/<id>/  official blanks  ──────────────▶ compared against
```

## The five layers

| Layer | Lives in | Holds | Never holds |
|---|---|---|---|
| **Study data** | `config.yml` | IRB no., titles, PI, dates, N, flags, phase | anything about the institution |
| **Institution profile** | `institutions/<id>/profile.yml` | names, IRB-number label, submission address, page size + margins, form font, where the blanks are | study data |
| **Form pack** | `institutions/<id>/forms.py` | `FORM_REGISTRY` (form id → name, generator) and `PHASE_FORMS` (routing rules) | layout constants |
| **Generators** | `blank_generator(...)` or a python-docx module | how one form gets its values | hardcoded names, emails, fonts (read `institution()`) |
| **Gate** | `scripts/validate_layout.py` | checks output against the blanks + profile | institution-specific code |

The scripts in `scripts/` (`generate_all`, `form_selector`, `docx_utils`,
`template_fill`, `validate_layout`, `fetch_templates`, `convert`, `checklist`)
are institution-agnostic. They read the active profile through
`scripts/institution.py` (`IRB_INSTITUTION` env var, then `institution:` in
`config.yml`, then `kfsyscc`).

## Two ways to generate a form

| | **Fill the blank** (`scripts/template_fill.py`) | **Rebuild** (python-docx, e.g. `scripts/generators/`) |
|---|---|---|
| How | copy the official blank, write values next to labels, flip □→■ | draw the form from scratch with `init_doc`, `add_header`, tables |
| Layout fidelity | exact: the official file is the output | must be tuned until the gate passes |
| Effort per form | a dict of `label → value` | 50 to 300 lines |
| Use when | the blank has stable labels or empty cells | the blank is a scanned PDF, uses text boxes or frames, or the output is mostly generated prose (e.g. a protocol summary) |

**Default to fill-the-blank** for a new institution. Rebuild only the forms
where filling can't work. Both kinds can coexist in one `FORM_REGISTRY`.

## Pipeline steps

1. **Harvest the blanks.** Use `make templates` (scraper driven by
   `templates.index_url`) or drop the files into `templates/<id>/`. Keep them
   untouched: they are the ground truth for the gate.
2. **Fingerprint each blank.** Run `make onboard INST=<id>`. It records the
   paper size, margins (`<w:sectPr>`), dominant CJK/Latin font, language tag,
   table labels, `label：＿＿` fill-in lines and checkbox options in
   `form_inventory.md`.
3. **Describe the institution once** in `profile.yml`. Anything that would
   otherwise be a string literal in a generator goes here.
4. **Map labels to study fields** in `forms.py`. Each label maps to a
   format string (`"{pi.name}（{pi.dept}）"`) or a callable. Each checkbox
   maps to a predicate on the config.
5. **Route.** In `PHASE_FORMS`, each phase lists its `base` forms plus
   `(predicate, [forms])` conditions such as *expedited → expedited-review checklist* or
   *consent waived → waiver form*. Mirror the institution's own submission
   checklist form; it is the routing spec.
6. **Generate → convert → gate.** `make all` runs `generate_all` (which applies the
   official page setup), then `convert` (PDF + PNG), then `validate_layout`. Ship only
   at **0 errors**, and submit the PDF.
7. **Close the loop.** Use `checklist.md` for the manual steps (signatures, attachments,
   sending). These come from the profile's `submission` block.

## Invariants (what keeps output identical on Windows and Mac)

- **Paper and margins come from the blank**, copied in twips (567 twips = 1 cm).
  python-docx defaults to US Letter with 3.17 cm sides, so every rebuilt form
  must go through `apply_official_page_setup`.
- **No theme fonts.** `minorEastAsia` resolves differently per OS and locale.
  `pin_form_font` rewrites docDefaults, styles and runs to the profile font and
  declares it in `fontTable.xml` with an `altName` (e.g. 標楷體 → DFKai-SB, which
  macOS ships as BiauKai).
- **Glyphs inside the font's encoding.** Set `font.encoding` (`cp950`
  for Big5 Kai/Ming fonts). Characters outside it trigger silent per-OS
  substitution, and the gate warns about them.
- **Checkbox glyphs**: ■ (U+25A0) checked, □ (U+25A1) unchecked, through
  `check()`. `template_fill` also recognises ☐/☑ in blanks.
- **The PDF is the submission copy** (fonts embedded). Send the DOCX only if
  the committee wants to edit it.

## DOCX pitfalls the engine already handles

| Pitfall | Handling |
|---|---|
| Word splits text into many runs (`□` and `簡易審查` in different runs) | checkbox matching works on the paragraph's joined text, then flips the glyph in whichever run holds it |
| Merged cells repeat in `row.cells` | fill targets the first *distinct* cell to the right, or the cell below if the label is last in its row |
| Legacy `.doc` | converted with LibreOffice headless (`fetch_templates`, `onboard`) |
| Labels with stray spaces or full-width colons | labels are compared with whitespace, `:` and `：` stripped |
| Blank has no East Asian language tag | onboarding defaults to `zh-TW` when CJK text is present (verify it) |
| Header/footer tables, nested tables | included in the label search |

Not handled automatically, so rebuild these forms or edit the blank: text boxes or frames
(`w:txbxContent`), content controls (`w:sdt`), legacy form fields
(`w:fldChar FORMTEXT`), and scanned or PDF-only forms.

## Adapting checklist

- [ ] Blanks in `templates/<id>/`, untouched
- [ ] `make onboard INST=<id>` → `profile.yml`, `forms.py`, `form_inventory.md`
- [ ] Every `TODO` in `profile.yml` resolved (names, email, font aliases, lang)
- [ ] Every label, fill-in line and checkbox in `form_inventory.md` mapped or deliberately left blank
- [ ] `PHASE_FORMS` mirrors the institution's own submission checklist
- [ ] `institution: <id>` in `config.yml`, `make all` passes with 0 errors
- [ ] Side-by-side previews in `output/preview/compare/` look right
- [ ] Any new config fields documented in `.claude/skills/irb/references/config-schema.md`

See [ONBOARDING.md](ONBOARDING.md) for the step-by-step fork guide.
