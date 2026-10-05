#!/usr/bin/env python3
"""Layout / font safety gate for generated IRB forms (run before submission).

For every DOCX in output/ it checks:

  1. Page setup   — paper size + margins match the official blank form
  2. Fonts        — every CJK run resolves to the profile's form font (no theme /
                    fallback fonts), language tagged, font declared in fontTable
                    with its altName (so Word for Windows *and* Mac find it)
  3. Glyphs       — no characters outside the font's encoding (e.g. Big5 for
                    標楷體), which Word on Win/Mac would silently substitute
  4. Template     — official wording (labels) of the blank form still present
  5. Render       — (LibreOffice) PDF fonts all embedded, page count does not
                    overflow the blank form, side-by-side preview PNG for eyeballing

Errors exit non-zero so `make all` stops before anything unsafe is sent.
Paper, margins, font and the blank forms all come from the active institution
profile (institutions/<id>/profile.toml); blanks are cached by `make templates`.

Usage: uv run python scripts/validate_layout.py [output_dir] [--no-render] [--strict]
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docx import Document
from docx.oxml.ns import qn

from scripts.convert import docx_to_pdf, find_soffice
from scripts.docx_utils import form_id_from_path, official_margins
from scripts.institution import current

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_TOL = 60                  # ~1 mm
MARGIN_TOL = 115               # ~2 mm
LABEL_COVERAGE_WARN = 0.5

CJK_RE = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f]")
MARGIN_KEYS = ("left", "right", "top", "bottom")
# PDF font names that mean the renderer had no Kai font and fell back
FALLBACK_FONT_HINTS = ("DejaVu", "WenQuanYi", "Droid", "Unifont", "Noto Sans",
                       "PingFang", "Heiti", "MingLiU", "PMingLiU", "SimSun")


class Report:
    def __init__(self, name):
        self.name = name
        self.errors, self.warnings, self.notes = [], [], []
        self.preview = None

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.notes.append(msg)


# ---------------------------------------------------------------------------
# DOCX helpers
# ---------------------------------------------------------------------------

def page_setup(doc):
    """First section's page size/margins in twips."""
    sect = doc.sections[0]._sectPr
    sz, mar = sect.find(qn("w:pgSz")), sect.find(qn("w:pgMar"))

    def get(el, attr):
        val = el.get(qn(f"w:{attr}")) if el is not None else None
        return int(val) if val else None

    return {
        "width": get(sz, "w"), "height": get(sz, "h"),
        "orient": sz.get(qn("w:orient")) if sz is not None else None,
        **{k: get(mar, k) for k in MARGIN_KEYS},
    }


def all_text(doc):
    parts = [t.text or "" for t in doc.element.body.iter(qn("w:t"))]
    for s in doc.sections:
        for hf in (s.header, s.footer):
            if not hf.is_linked_to_previous:
                parts += [t.text or "" for t in hf._element.iter(qn("w:t"))]
    return "".join(parts)


class FontResolver:
    """Resolve the effective eastAsia/ascii font of a run (run → styles → docDefaults)."""

    def __init__(self, doc):
        self.styles = {}
        for st in doc.styles.element.findall(qn("w:style")):
            self.styles[st.get(qn("w:styleId"))] = st
        self.default_para = next((sid for sid, st in self.styles.items()
                                  if st.get(qn("w:type")) == "paragraph"
                                  and st.get(qn("w:default")) == "1"), None)
        dd = doc.styles.element.find(qn("w:docDefaults"))
        rpr = dd.find(qn("w:rPrDefault")) if dd is not None else None
        rpr = rpr.find(qn("w:rPr")) if rpr is not None else None
        self.defaults = rpr.find(qn("w:rFonts")) if rpr is not None else None

    @staticmethod
    def _font(rfonts, slot):
        """Return (font, source) from one rFonts element, theme counts as a font."""
        if rfonts is None:
            return None
        if rfonts.get(qn(f"w:{slot}")):
            return rfonts.get(qn(f"w:{slot}"))
        theme = rfonts.get(qn(f"w:{slot}Theme")) or (
            rfonts.get(qn("w:cstheme")) if slot == "cs" else None)
        return f"theme:{theme}" if theme else None

    def _style_chain(self, sid):
        seen = set()
        while sid and sid in self.styles and sid not in seen:
            seen.add(sid)
            st = self.styles[sid]
            yield st
            based = st.find(qn("w:basedOn"))
            sid = based.get(qn("w:val")) if based is not None else None

    def resolve(self, run, slot):
        rpr = run.find(qn("w:rPr"))
        chain = [rpr.find(qn("w:rFonts")) if rpr is not None else None]
        rstyle = rpr.find(qn("w:rStyle")) if rpr is not None else None
        if rstyle is not None:
            chain += [st.find(qn("w:rPr")) for st in self._style_chain(rstyle.get(qn("w:val")))]
        p = run.getparent()
        while p is not None and p.tag != qn("w:p"):
            p = p.getparent()
        ppr = p.find(qn("w:pPr")) if p is not None else None
        pstyle = ppr.find(qn("w:pStyle")) if ppr is not None else None
        sid = pstyle.get(qn("w:val")) if pstyle is not None else self.default_para
        chain += [st.find(qn("w:rPr")) for st in self._style_chain(sid)]
        for el in chain:
            if el is None:
                continue
            rf = el if el.tag == qn("w:rFonts") else el.find(qn("w:rFonts"))
            f = self._font(rf, slot)
            if f:
                return f
        return self._font(self.defaults, slot) or "(application default)"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_page(doc, tpl_doc, fid, rep):
    g = page_setup(doc)
    if g["orient"] == "landscape" or (g["width"] and g["height"] and g["width"] > g["height"]):
        rep.warn("頁面為橫向 (landscape)")
    size = (g["width"], g["height"])
    ref_size = (current().page["width"], current().page["height"])
    ref_margins = dict(zip(MARGIN_KEYS, official_margins(fid), strict=True))
    if tpl_doc is not None:
        t = page_setup(tpl_doc)
        ref_size = (t["width"], t["height"])
        ref_margins = {k: t[k] for k in MARGIN_KEYS}
    if any(v is None for v in size) or any(abs(a - b) > PAGE_TOL for a, b in zip(sorted(size), sorted(ref_size), strict=True)):
        rep.error(f"紙張大小 {fmt_cm(size)} ≠ 官方表單 {fmt_cm(ref_size)}（紙張不符會在 Win/Mac 列印時縮放跑版）")
    off = [f"{k} {g[k] / 567:.2f}→{ref_margins[k] / 567:.2f}cm" for k in MARGIN_KEYS
           if g[k] is None or ref_margins[k] is None or abs(g[k] - ref_margins[k]) > MARGIN_TOL]
    if off:
        rep.warn("邊界與官方表單不同：" + "、".join(off))


def fmt_cm(size):
    return "×".join(f"{v / 567:.1f}" if v else "?" for v in size) + "cm"


def check_fonts(doc, rep):
    res = FontResolver(doc)
    font = current().font
    bad_cjk, bad_latin = {}, {}
    elements = [doc.element.body] + [hf._element for s in doc.sections
                                     for hf in (s.header, s.footer) if not hf.is_linked_to_previous]
    for root in elements:
        for r in root.iter(qn("w:r")):
            text = "".join(t.text or "" for t in r.iter(qn("w:t")))
            if not text.strip():
                continue
            if CJK_RE.search(text):
                f = res.resolve(r, "eastAsia")
                if f not in current().font_aliases:
                    bad_cjk.setdefault(f, text.strip()[:20])
            if re.search(r"[A-Za-z0-9]", text):
                f = res.resolve(r, "ascii")
                if f.startswith("theme:") or f.startswith("("):
                    bad_latin.setdefault(f, text.strip()[:20])
    for f, sample in bad_cjk.items():
        rep.error(f"中文字型為「{f}」而非{font['name']}（例：「{sample}」）— Win/Mac 會顯示不同字型")
    for f, sample in bad_latin.items():
        rep.warn(f"英數字型依賴佈景主題「{f}」（例：「{sample}」）— Win/Mac 預設不同")

    dd_lang = doc.styles.element.find(qn("w:docDefaults"))
    lang = dd_lang.find(".//" + qn("w:lang")) if dd_lang is not None else None
    want_lang = font.get("lang", "zh-TW")
    if lang is None or lang.get(qn("w:eastAsia")) != want_lang:
        rep.warn(f"文件東亞語言未設為 {want_lang} — 標點擠壓/斷行規則在 Win/Mac 可能不同")

    font_table = next((p for p in doc.part.package.iter_parts()
                       if str(p.partname) == "/word/fontTable.xml"), None)
    blob = font_table.blob.decode("utf-8", "replace") if font_table is not None else ""
    alt = (font.get("aliases") or [None])[0]
    if f'w:name="{font["name"]}"' not in blob:
        rep.warn(f"fontTable 未宣告{font['name']} — 缺字型時 Word 無替代提示")
    elif alt and alt not in blob:
        rep.warn(f"fontTable 的{font['name']}缺 altName {alt} — Mac/英文版 Word 可能找不到")


def check_glyphs(text, rep):
    font = current().font
    enc = font.get("encoding")
    if not enc:
        return
    odd = sorted({c for c in text if ord(c) > 127 and not _in_encoding(c, enc)})
    if odd:
        sample = "".join(odd[:15])
        label = "Big5" if enc.lower() in ("cp950", "big5") else enc
        rep.warn(f"{len(odd)} 個字元超出 {label}（{font['name']}可能缺字，Win/Mac 會各自補字型）："
                 f"{sample} — 請在 PDF 確認字體一致")


def _in_encoding(ch, enc):
    try:
        ch.encode(enc)
        return True
    except UnicodeEncodeError:
        return False


LABEL_SPLIT_RE = re.compile(r"[\s□■☐☑✓✔_＿:：,，、。.;；()（）\[\]【】「」/／\-–—|]+")


def _norm(s):
    return re.sub(r"[\s□■☐☑_＿:：]", "", s)


def template_labels(tpl_doc):
    """Short CJK phrases of the blank form = its fixed wording."""
    labels = []
    for chunk in LABEL_SPLIT_RE.split(all_text_by_paragraph(tpl_doc)):
        if 2 <= len(chunk) <= 20 and len(CJK_RE.findall(chunk)) >= 2 and chunk not in labels:
            labels.append(chunk)
    return labels


def all_text_by_paragraph(doc):
    return "\n".join("".join(t.text or "" for t in p.iter(qn("w:t")))
                     for p in doc.element.body.iter(qn("w:p")))


def check_labels(doc, tpl_doc, rep):
    labels = template_labels(tpl_doc)
    if not labels:
        return
    gen = _norm(all_text(doc))
    missing = [label for label in labels if _norm(label) not in gen]
    cov = 1 - len(missing) / len(labels)
    msg = f"官方表單文字涵蓋率 {cov:.0%}（{len(labels) - len(missing)}/{len(labels)}）"
    if cov < LABEL_COVERAGE_WARN:
        rep.warn(msg + "；缺：" + "、".join(missing[:8]) + ("…" if len(missing) > 8 else ""))
    else:
        rep.note(msg)


# ---------------------------------------------------------------------------
# Render checks (LibreOffice + poppler)
# ---------------------------------------------------------------------------

def pdf_pages(pdf):
    try:
        from pdf2image import pdfinfo_from_path
        return int(pdfinfo_from_path(pdf)["Pages"])
    except Exception:
        return None


def pdf_fonts(pdf):
    """[(name, embedded)] via poppler's pdffonts, or None if unavailable."""
    exe = shutil.which("pdffonts")
    if not exe:
        return None
    out = subprocess.run([exe, pdf], capture_output=True, text=True).stdout.splitlines()
    fonts = []
    for line in out[2:]:
        cols = line.split()
        # name type [encoding…] emb sub uni object ID  → emb is 5th from the end
        if len(cols) >= 7:
            fonts.append((cols[0].split("+")[-1], cols[-5] == "yes"))
    return fonts


def template_pdf(fid):
    pdf_dir = os.path.join(current().template_dir, "pdf")
    pdf = os.path.join(pdf_dir, f"{fid}.pdf")
    src = current().blank_path(fid)
    if not os.path.exists(pdf) and os.path.exists(src):
        os.makedirs(pdf_dir, exist_ok=True)
        docx_to_pdf(src, pdf_dir)
    return pdf if os.path.exists(pdf) else None


def check_render(docx_path, fid, tmp_dir, compare_dir, rep):
    pdf = docx_to_pdf(docx_path, tmp_dir)
    if not pdf:
        rep.error("LibreOffice 無法轉成 PDF（檔案可能損毀）")
        return
    fonts = pdf_fonts(pdf)
    if fonts is not None:
        not_emb = sorted({n for n, emb in fonts if not emb})
        if not_emb:
            rep.error("PDF 有未嵌入字型：" + "、".join(not_emb) + "（對方電腦會換字型）")
        fallback = sorted({n for n, _ in fonts if any(h.lower() in n.lower() for h in FALLBACK_FONT_HINTS)})
        if fallback:
            rep.warn("轉檔時字型被替換為：" + "、".join(fallback) + "（本機沒有" + current().font["name"] + " → 預覽排版不準）")
    pages = pdf_pages(pdf)
    tpl_pdf = template_pdf(fid) if fid else None
    tpl_pages = pdf_pages(tpl_pdf) if tpl_pdf else None
    if pages and tpl_pages:
        limit = max(tpl_pages, current().templates.get("max_pages", {}).get(fid, 0))
        if pages > limit:
            rep.warn(f"頁數 {pages} > 官方空白表單 {tpl_pages} 頁 — 確認沒有表格被擠到下一頁")
        else:
            rep.note(f"頁數 {pages}（官方 {tpl_pages}）")
    elif pages:
        rep.note(f"頁數 {pages}")
    if tpl_pdf:
        rep.preview = side_by_side(tpl_pdf, pdf, os.path.join(compare_dir, f"{fid}.png"))


def side_by_side(tpl_pdf, gen_pdf, out_png, dpi=80):
    """Official blank (left) vs generated (right), page 1, for human eyeballing."""
    try:
        from pdf2image import convert_from_path
        from PIL import Image, ImageDraw
        left = convert_from_path(tpl_pdf, dpi=dpi, first_page=1, last_page=1)[0]
        right = convert_from_path(gen_pdf, dpi=dpi, first_page=1, last_page=1)[0]
        gap, bar = 20, 24
        w, h = left.width + right.width + gap, max(left.height, right.height) + bar
        canvas = Image.new("RGB", (w, h), "white")
        canvas.paste(left, (0, bar))
        canvas.paste(right, (left.width + gap, bar))
        d = ImageDraw.Draw(canvas)
        d.text((8, 6), "OFFICIAL BLANK", fill="black")
        d.text((left.width + gap + 8, 6), "GENERATED", fill="black")
        os.makedirs(os.path.dirname(out_png), exist_ok=True)
        canvas.save(out_png)
        return out_png
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def load_template(fid):
    if not fid:
        return None
    path = current().blank_path(fid)
    if not os.path.exists(path):
        return None
    try:
        return Document(path)
    except Exception:
        return None


def validate_file(path, render=False, tmp_dir=None, compare_dir=None):
    rep = Report(os.path.basename(path))
    try:
        doc = Document(path)
    except Exception as e:
        rep.error(f"無法開啟 DOCX：{e}")
        return rep
    fid = form_id_from_path(path)
    tpl = load_template(fid)
    if fid and tpl is None:
        rep.note("無官方空白表單快取（執行 make templates）— 僅檢查紙張/字型")
    check_page(doc, tpl, fid, rep)
    check_fonts(doc, rep)
    check_glyphs(all_text(doc), rep)
    if tpl is not None:
        check_labels(doc, tpl, rep)
    if render:
        check_render(path, fid, tmp_dir, compare_dir, rep)
    return rep


def write_markdown(reports, path, render):
    lines = ["# 排版安全檢查報告 (Layout Validation)", "",
             "■ = 通過　□ = 需處理　⚠ = 請人工確認", "",
             "| 表單 | 結果 | 錯誤 | 警告 |", "|---|---|---|---|"]
    for r in reports:
        status = "□ 錯誤" if r.errors else ("⚠ 警告" if r.warnings else "■ 通過")
        lines.append(f"| {r.name} | {status} | {len(r.errors)} | {len(r.warnings)} |")
    for r in reports:
        lines += ["", f"## {r.name}", ""]
        lines += [f"- □ {m}" for m in r.errors]
        lines += [f"- ⚠ {m}" for m in r.warnings]
        lines += [f"- ■ {m}" for m in r.notes]
        if r.preview:
            lines.append(f"- 對照圖：`{os.path.relpath(r.preview, os.path.dirname(path))}`")
    lines += ["", "## 送件前人工確認", "",
              "- □ 開啟 `preview/compare/*.png`，左右比對表格框線、欄寬、標題位置",
              "- □ 交件以 **PDF**（字型已嵌入）為準；DOCX 僅供 IRB 需要修改時使用",
              "- □ 若對方要 DOCX：在 Windows Word 與 Mac Word 各開一次，確認字型顯示為" + current().font["name"],
              ""]
    if not render:
        lines.insert(4, "> 本次未進行 PDF 轉檔檢查（--no-render 或缺 LibreOffice）\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main(output_dir="output", render=True, strict=False):
    files = sorted(glob.glob(os.path.join(output_dir, "*.docx")))
    if not files:
        print(f"No .docx files in {output_dir}/ — run `make generate` first")
        return 1
    if render and not find_soffice():
        print("⚠ LibreOffice not found — skipping render checks (PDF fonts, page count)")
        render = False
    if not os.path.exists(os.path.join(current().template_dir, "index.json")):
        print("⚠ Official blank forms not cached — run `make templates` for template comparison")

    compare_dir = os.path.join(output_dir, "preview", "compare")
    print(f"Validating {len(files)} forms (render={'on' if render else 'off'})...\n")
    with tempfile.TemporaryDirectory() as tmp:
        reports = [validate_file(f, render, tmp, compare_dir) for f in files]

    for r in reports:
        mark = "✗" if r.errors else ("⚠" if r.warnings else "■")
        print(f"  {mark} {r.name}")
        for m in r.errors:
            print(f"      ERROR  {m}")
        for m in r.warnings:
            print(f"      WARN   {m}")

    report_path = os.path.join(output_dir, "layout_report.md")
    write_markdown(reports, report_path, render)
    n_err = sum(len(r.errors) for r in reports)
    n_warn = sum(len(r.warnings) for r in reports)
    print(f"\n{'═' * 46}")
    print(f"  Errors: {n_err}  Warnings: {n_warn}")
    print(f"  Report: {report_path}")
    print(f"{'═' * 46}")
    return 1 if n_err or (strict and n_warn) else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sys.exit(main(args[0] if args else "output",
                  render="--no-render" not in sys.argv,
                  strict="--strict" in sys.argv))
