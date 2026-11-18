"""Fill an official blank DOCX in place — the institution-agnostic generator.

Instead of rebuilding a form with python-docx, copy the institution's own blank
and write values next to its labels. Layout, margins, headers (版次/編修日期),
fonts and wording stay exactly the official ones, so the layout gate passes by
construction.

Declarative (most forms):

    from irb_in_hurry.template_fill import blank_generator

    generate_f01 = blank_generator("F01", fields={
        "計畫名稱": "{study.title_zh}",           # label → format string
        "計畫主持人": "{pi.name}",
        "預計收案人數": lambda c: f"{c['subjects']['planned_n']} 人",
    }, checks={
        "簡易審查": lambda c: c["study"]["review_type"] == "expedited",
    })

fields: label text → value. The value goes into the next table cell to the
        right of the label (or below it if the label is the last cell), or
        replaces the blank (＿＿ / ____ / spaces) after the label in a paragraph.
checks: option text → bool. A ☐/□ right before the option becomes ■ when true.

Imperative (forms with repeated options, optional rows or appendices) — `Form`:

    form = Form(blank)
    row = form.row("1.申請型態")                 # scope = one table row
    form.check("簡易審查", scope=row)             # first □ before that option
    form.check("否", scope=row, after="(3)")      # first □否 after a sub-question
    form.put("姓名", "王小明", scope=row)         # fill the blank after a label
    form.cell("計畫主持人", "王小明")              # label cell → cell on its right
    form.delete_row(form.row("研究人員"))
    form.delete_between("(附表一)", "(附表四)")    # drop body blocks
    form.save(out)

Symbol-font checkboxes (Wingdings `w:sym` and private-use characters typed into
the text) are rewritten to □ / ■ / √ in the form font first: renderers without
Wingdings draw them as ☒, which reads as *checked*.
"""
import copy
import os
import re
import shutil
import unicodedata

from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Pt
from docx.text.run import Run

from irb_in_hurry.docx_utils import check, form_font, pin_form_font, strip_theme_fonts
from irb_in_hurry.institution import current

BOXES = "□☐■☑"
_BLANK_RE = re.compile(r"[＿_]{2,}|[ \t　]{3,}")
_WS = r"[ \t　]*"
_WS_RE = re.compile(r"[\s　:：]+")
_RUN_XPATH = "./w:r | ./w:hyperlink/w:r | ./w:smartTag/w:r | ./w:ins/w:r | ./w:fldSimple/w:r"


def _norm(text):
    return _WS_RE.sub("", text or "")


def _flex(text):
    """Regex for text that tolerates spacing inside it ('對 照 組') and ：/: variants."""
    parts = []
    for ch in text.strip():
        if ch.isspace():
            continue
        parts.append("[:：]" if ch in ":：" else re.escape(ch))
    return _WS.join(parts)


# ---------------------------------------------------------------------------
# Symbol-font glyphs → Unicode in the form font
# ---------------------------------------------------------------------------

# Wingdings / Wingdings 2 code points used as checkboxes in official blanks.
WINGDINGS = {
    0xF0A3: "□", 0xF0A8: "□", 0xF06F: "□", 0xF0A1: "□", 0xF071: "□",
    0xF0FC: "√", 0xF0FE: "■", 0xF052: "■",
}
# Symbol-font math glyphs, mapped to their Big5 (full-width) equivalents.
SYMBOL = {0xF0A3: "≦", 0xF0B3: "≧", 0xF0B1: "±", 0xF0B4: "×"}


def _symbol_table(font):
    font = (font or "").lower()
    if font.startswith("wingdings"):
        return WINGDINGS
    if font == "symbol":
        return SYMBOL
    return None


def _run_font(r):
    rpr = r.find(qn("w:rPr"))
    rf = rpr.find(qn("w:rFonts")) if rpr is not None else None
    if rf is None:
        return ""
    return rf.get(qn("w:ascii")) or rf.get(qn("w:hAnsi")) or rf.get(qn("w:cs")) or ""


def _pin_run_font(r):
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        rpr = parse_xml(f'<w:rPr {nsdecls("w")}/>')
        r.insert(0, rpr)
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = parse_xml(f'<w:rFonts {nsdecls("w")}/>')
        rpr.insert(0, rf)
    for attr in list(rf.attrib):
        del rf.attrib[attr]
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), form_font())


def normalize_symbols(doc):
    """Rewrite Wingdings/Symbol checkboxes and math glyphs as Unicode in the form font.

    Covers `<w:sym w:font="Wingdings 2" w:char="F0A3"/>` and private-use
    characters (U+F0xx) typed straight into the text. Returns the number fixed."""
    roots = [doc.element.body] + [hf._element for s in doc.sections
                                  for hf in (s.header, s.footer, s.first_page_header,
                                             s.first_page_footer, s.even_page_header,
                                             s.even_page_footer)
                                  if hf._has_definition]
    fixed = 0
    for root in roots:
        # CJK compatibility ideographs (U+F900–FAFF, left by .doc conversion) are
        # outside Big5: NFC maps them to the unified ideograph the font has.
        for t in root.iter(qn("w:t")):
            if t.text and any(0xF900 <= ord(c) <= 0xFAFF for c in t.text):
                t.text = unicodedata.normalize("NFC", t.text)
                fixed += 1
        for sym in list(root.iter(qn("w:sym"))):
            table = _symbol_table(sym.get(qn("w:font")))
            try:
                code = int(sym.get(qn("w:char")) or "", 16)
            except ValueError:
                continue
            code = code if code >= 0xF000 else code + 0xF000
            if table is None or code not in table:
                continue
            t = parse_xml(f'<w:t {nsdecls("w")} xml:space="preserve"/>')
            t.text = table[code]
            sym.addprevious(t)
            sym.getparent().remove(sym)
            _pin_run_font(t.getparent())
            fixed += 1
        for t in root.iter(qn("w:t")):
            text = t.text or ""
            if not any(0xF000 <= ord(c) <= 0xF0FF for c in text):
                continue
            r = t.getparent()
            table = _symbol_table(_run_font(r)) or WINGDINGS
            new = "".join(table.get(ord(c), c) if 0xF000 <= ord(c) <= 0xF0FF else c for c in text)
            if new != text:
                fixed += sum(1 for a, b in zip(text, new, strict=True) if a != b)
                t.text = new
                _pin_run_font(r)
    return fixed


# ---------------------------------------------------------------------------
# Run-aware paragraph editing
# ---------------------------------------------------------------------------

def _runs(p):
    return [Run(r, None) for r in p.xpath(_RUN_XPATH)]


def _ptext(p):
    return "".join(r.text for r in _runs(p))


def _splice(p, start, end, new):
    """Replace characters [start, end) of a paragraph's text with `new`.

    Surrounding text keeps its runs; `new` becomes a run of its own (formatted
    like its neighbour, font pinned to the form font) so values and ■ never
    inherit a symbol or Latin-only font from the blank."""
    runs, pos, segs = _runs(p), 0, []
    for r in runs:
        t = r.text
        segs.append((r, pos, pos + len(t), t))
        pos += len(t)
    host = None
    for r, a, b, t in segs:
        if not t:
            continue
        if start == end:
            if a <= start <= b:
                host, cut_lo, cut_hi = (r, a, t), start - a, start - a
                break
            continue
        lo, hi = max(a, start), min(b, end)
        if lo >= hi:
            continue
        if host is None:
            host, cut_lo, cut_hi = (r, a, t), lo - a, hi - a
        else:
            r.text = t[:lo - a] + t[hi - a:]
    if host is None:
        if new:
            _pin_run_font(_append_run(p, new))
        return
    r, a, t = host
    before, after = t[:cut_lo], t[cut_hi:]
    r.text = before
    if new:
        mid = copy.deepcopy(r._r)
        r._r.addnext(mid)
        Run(mid, None).text = new
        _pin_run_font(mid)
        anchor = mid
    else:
        anchor = r._r
    if after:
        tail = copy.deepcopy(r._r)
        anchor.addnext(tail)
        Run(tail, None).text = after


def _append_run(p, text):
    """Append a run formatted like the paragraph's last run (or its paragraph mark)."""
    runs = p.xpath("./w:r")
    rpr = None
    if runs and runs[-1].find(qn("w:rPr")) is not None:
        rpr = copy.deepcopy(runs[-1].find(qn("w:rPr")))
    else:
        mark = p.find(qn("w:pPr"))
        mark = mark.find(qn("w:rPr")) if mark is not None else None
        if mark is not None:
            rpr = copy.deepcopy(mark)
            for bad in rpr.findall(qn("w:rStyle")):
                rpr.remove(bad)
    r = parse_xml(f'<w:r {nsdecls("w")}/>')
    if rpr is not None:
        r.append(rpr)
    p.append(r)
    Run(r, None).text = text
    return r


def _set_paragraph_text(p, text):
    runs = _runs(p)
    if not runs:
        _pin_run_font(_append_run(p, text))
        return
    runs[0].text = text
    _pin_run_font(runs[0]._r)
    for r in runs[1:]:
        r.text = ""


class Form:
    """An official blank opened for filling. See the module docstring."""

    def __init__(self, path):
        self.path = path
        self.doc = Document(path)
        self.body = self.doc.element.body
        self.missing = []
        normalize_symbols(self.doc)

    # -- scopes -------------------------------------------------------------

    def paragraphs(self, scope=None):
        """w:p elements of a scope (a row/cell/table element, a list of them, or the body)."""
        if scope is None:
            scope = self.body
        if isinstance(scope, list):
            return [p for s in scope for p in self.paragraphs(s)]
        if scope.tag == qn("w:p"):
            return [scope]
        return list(scope.iter(qn("w:p")))

    def row(self, anchor, nth=0, head=False):
        """The innermost table row whose text contains `anchor` (nth match), or None.

        head=True matches only the row's first cell (its label column)."""
        want = _norm(anchor)

        def text(tr):
            el = tr.find(qn("w:tc")) if head else tr
            return _norm("".join(t.text or "" for t in el.iter(qn("w:t")))) if el is not None else ""

        rows = [tr for tr in self.body.iter(qn("w:tr")) if want in text(tr)]
        # an outer row containing a nested table also matches: keep the innermost
        inner = [tr for tr in rows if not any(o is not tr and o in tr.iter() for o in rows)]
        if len(inner) <= nth:
            self.missing.append(f"row:{anchor}")
            return None
        return inner[nth]

    def table(self, anchor):
        """The table (w:tbl) that holds `anchor`."""
        tr = self.row(anchor)
        return tr.getparent() if tr is not None else None

    # -- edits --------------------------------------------------------------

    def check(self, option, on=True, scope=None, after=None, every=False):
        """Mark the □ in front of `option` (■ if on). `after`: only past that text."""
        pat = re.compile(rf"[{BOXES}](?={_WS}{_flex(option)})")
        hit = False
        armed = after is None
        for p in self.paragraphs(scope):
            text = _ptext(p)
            start = 0
            if not armed:
                m = re.search(_flex(after), text)
                if not m:
                    continue
                armed, start = True, m.end()
            for m in pat.finditer(text, start):
                _splice(p, m.start(), m.end(), check(on))
                hit = True
                if not every:
                    return True
        if not hit:
            self.missing.append(f"□{option}")
        return hit

    def put(self, label, value, scope=None, after=None):
        """Write `value` into the blank after `label` (or right after its colon)."""
        value = str(value)
        armed = after is None
        for p in self.paragraphs(scope):
            text = _ptext(p)
            start = 0
            if not armed:
                m = re.search(_flex(after), text)
                if not m:
                    continue
                armed, start = True, m.end()
            m = re.compile(_flex(label)).search(text, start)
            if not m:
                continue
            pos = m.end()
            colon = re.match(r"[ \t　]*[:：]", text[pos:])
            if colon:
                pos += colon.end()
            blank = re.match(r"[ \t\u3000]*[＿_]+|[ \t\u3000]{2,}", text[pos:])
            if blank and blank.end():
                rest = text[pos + blank.end():]
                # keep a gap before the next label when the blank was plain spacing
                pad = "　" if rest.strip() and not re.search("[＿_]", blank.group()) else ""
                _splice(p, pos, pos + blank.end(), value + pad)
            else:
                _splice(p, pos, pos, value)
            return True
        self.missing.append(label)
        return False

    def sub(self, pattern, repl, scope=None, count=1):
        """Regex replace inside paragraphs (run-aware). Returns number of replacements."""
        rx = re.compile(pattern)
        done = 0
        for p in self.paragraphs(scope):
            for m in reversed(list(rx.finditer(_ptext(p)))):
                _splice(p, m.start(), m.end(), m.expand(repl))
                done += 1
                if count and done >= count:
                    return done
        if not done:
            self.missing.append(f"/{pattern}/")
        return done

    def cell(self, label, value, scope=None, nth=0, size=None):
        """Fill the cell right of the cell whose text is `label` (or the one below)."""
        want = _norm(label)
        found = 0
        root = self.body if scope is None else scope
        for tr in root.iter(qn("w:tr")):
            tcs = tr.findall(qn("w:tc"))
            for i, tc in enumerate(tcs):
                if _norm("".join(t.text or "" for t in tc.iter(qn("w:t")))) != want:
                    continue
                if found < nth:
                    found += 1
                    continue
                target = tcs[i + 1] if i + 1 < len(tcs) else None
                if target is None:
                    nxt = tr.getnext()
                    cells = nxt.findall(qn("w:tc")) if nxt is not None else []
                    target = cells[i] if i < len(cells) else None
                if target is not None:
                    self.set_cell(target, value, size=size)
                    return True
        self.missing.append(label)
        return False

    def set_cell(self, tc, value, size=None):
        """Replace a cell's text (keeps the first paragraph's formatting; size in pt)."""
        paras = tc.findall(qn("w:p"))
        # a blank cell justified "distribute" spreads a value across the width
        for jc in paras[0].iter(qn("w:jc")):
            if jc.get(qn("w:val")) in ("distribute", "thaiDistribute"):
                jc.set(qn("w:val"), "left")
        lines = str(value).split("\n")
        _set_paragraph_text(paras[0], lines[0])
        for extra in paras[1:]:
            tc.remove(extra)
        prev = paras[0]
        for line in lines[1:]:
            prev = self.insert_after(prev, line)
        if size:
            for r in tc.iter(qn("w:r")):
                Run(r, None).font.size = Pt(size)

    def insert_after(self, p, text, like=None):
        """New paragraph after `p`, formatted like `like` (default `p`). Returns it."""
        new = self._clone_paragraph(like if like is not None else p, text)
        p.addnext(new)
        return new

    def insert_before(self, p, text, like=None):
        new = self._clone_paragraph(like if like is not None else p, text)
        p.addprevious(new)
        return new

    @staticmethod
    def _clone_paragraph(src, text):
        new = copy.deepcopy(src)
        for child in list(new):
            if child.tag != qn("w:pPr"):
                new.remove(child)
        ppr = new.find(qn("w:pPr"))
        if ppr is not None:
            for num in ppr.findall(qn("w:numPr")):
                ppr.remove(num)
        src_runs = src.xpath("./w:r[w:t]")
        r = parse_xml(f'<w:r {nsdecls("w")}/>')
        if src_runs and src_runs[0].find(qn("w:rPr")) is not None:
            r.append(copy.deepcopy(src_runs[0].find(qn("w:rPr"))))
        elif ppr is not None and ppr.find(qn("w:rPr")) is not None:
            rpr = copy.deepcopy(ppr.find(qn("w:rPr")))
            for bad in rpr.findall(qn("w:rStyle")):
                rpr.remove(bad)
            r.append(rpr)
        new.append(r)
        Run(r, None).text = text
        _pin_run_font(r)
        return new

    def delete_row(self, tr):
        if tr is not None and tr.getparent() is not None:
            tr.getparent().remove(tr)

    def clone_row(self, tr):
        """Duplicate a table row right below itself. Returns the copy."""
        new = copy.deepcopy(tr)
        tr.addnext(new)
        return new

    def delete_between(self, start, end=None):
        """Remove body-level blocks from the paragraph containing `start` up to (not incl.)
        the next paragraph containing `end` (or the end of the document)."""
        children = [c for c in self.body if c.tag != qn("w:sectPr")]

        def hit(c, anchor):
            return c.tag == qn("w:p") and _norm(anchor) in _norm(_ptext(c))

        i = next((k for k, c in enumerate(children) if hit(c, start)), None)
        if i is None:
            self.missing.append(f"block:{start}")
            return 0
        j = len(children)
        if end is not None:
            j = next((k for k in range(i + 1, len(children)) if hit(children[k], end)), j)
        for c in children[i:j]:
            # keep a section break that rides on a paragraph
            if c.find(f"{qn('w:pPr')}/{qn('w:sectPr')}") is None:
                self.body.remove(c)
        return j - i

    def find_paragraph(self, anchor, scope=None):
        rx = re.compile(_flex(anchor))
        return next((p for p in self.paragraphs(scope) if rx.search(_ptext(p))), None)

    # -- output -------------------------------------------------------------

    def save(self, out_path):
        pin_form_font(self.doc)       # theme fonts render differently on Windows vs Mac
        strip_theme_fonts(self.doc)
        self.doc.save(out_path)
        return out_path


# ---------------------------------------------------------------------------
# Declarative interface
# ---------------------------------------------------------------------------

def _lookup(config, dotted):
    node = config
    for key in dotted.split("."):
        if isinstance(node, list):
            node = node[int(key)]
        elif isinstance(node, dict):
            node = node.get(key, "")
        else:
            return ""
    return "" if node is None else node


def resolve(value, config):
    """'{pi.name}（{pi.dept}）' / callable / literal → str."""
    if callable(value):
        return str(value(config))
    return re.sub(r"\{([\w.]+)\}", lambda m: str(_lookup(config, m.group(1))), str(value))


def fill_blank(blank_path, out_path, fields=None, checks=None, config=None):
    """Copy blank → out_path and fill it. Returns list of labels not found."""
    shutil.copyfile(blank_path, out_path)
    form = Form(out_path)
    for label, value in (fields or {}).items():
        text = resolve(value, config or {})
        if not form.cell(label, text):
            form.missing.pop()
            form.put(label, text)
    for option, cond in (checks or {}).items():
        on = bool(cond(config) if callable(cond) else cond)
        if not form.check(option, on, every=True):
            form.missing[-1] = f"{check(True)}{option}"
    form.save(out_path)
    return form.missing


def blank_path_or_none(form_id):
    """Path of the cached official blank for form_id, or None."""
    path = current().blank_path(form_id)
    return path if path and os.path.exists(path) else None


def blank_generator(form_id, fields=None, checks=None, filename="{form_id}_{study.irb_no}.docx"):
    """Build a `generate(config, output_dir) -> path` for one official blank."""
    def generate(config, output_dir):
        blank = blank_path_or_none(form_id)
        if blank is None:
            raise FileNotFoundError(f"No blank for {form_id}: {current().blank_path(form_id)} "
                                    f"(run `irbh templates`, or map it in templates.files)")
        name = resolve(filename.replace("{form_id}", form_id), config) or f"{form_id}.docx"
        out = os.path.join(output_dir, name)
        missing = fill_blank(blank, out, fields, checks, config)
        if missing:
            print(f"    ⚠ {form_id}: labels not found in blank: {', '.join(missing)}")
        return out
    generate.__name__ = f"generate_{form_id.lower()}"
    return generate
