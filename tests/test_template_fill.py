"""Form: the official-blank filler (symbol glyphs, scoped checks, rows, blocks) + gate checks."""
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

from irb_in_hurry import validate_layout
from irb_in_hurry.template_fill import Form, _ptext, normalize_symbols


def _sym(paragraph, font, char):
    r = paragraph.add_run()
    r._r.append(parse_xml(f'<w:sym {nsdecls("w")} w:font="{font}" w:char="{char}"/>'))


def make_blank(path):
    doc = Document()
    doc.sections[0].header.paragraphs[0].text = "版    次：第12版  編修日期：2026/03/02"
    p = doc.add_paragraph()
    _sym(p, "Wingdings 2", "F0A3")                     # Wingdings box (w:sym)
    p.add_run("無任何需揭露")
    p = doc.add_paragraph()
    r = p.add_run("有顯著財務利益")              # private-use box typed in the text
    r.font.name = "Wingdings 2"
    p = doc.add_paragraph("劑量")
    _sym(p, "Symbol", "F0A3")                          # Symbol ≤, not a box
    p.add_run("1 mSv　不良反應")                          # 不 = U+F967 compatibility ideograph
    tbl = doc.add_table(rows=3, cols=2)
    tbl.cell(0, 0).text = "1.申請型態"
    tbl.cell(0, 1).text = "□一般審查　□簡易審查"
    tbl.cell(1, 0).text = "協同主持人"
    tbl.cell(1, 1).text = "姓名：           簽名："
    tbl.cell(2, 0).text = "(3)是否成年"
    tbl.cell(2, 1).text = "□是 □否 (4)是否健康 □是 □否"
    doc.add_paragraph("(附表一)")
    doc.add_paragraph("試驗藥品簡介")
    doc.add_paragraph("(附表四)")
    doc.add_paragraph("基因研究簡介")
    doc.save(path)


def test_symbols_become_unicode_in_form_font(tmp_path):
    make_blank(tmp_path / "b.docx")
    doc = Document(tmp_path / "b.docx")
    assert normalize_symbols(doc) >= 3
    text = [p.text for p in doc.paragraphs]
    assert text[0] == "□無任何需揭露" and text[1] == "□有顯著財務利益"
    assert text[2] == "劑量≦1 mSv　不良反應"          # Big5 ≦, NFC 不
    assert not list(doc.element.body.iter(qn("w:sym")))
    fonts = {rf.get(qn("w:eastAsia")) for rf in doc.paragraphs[1]._p.iter(qn("w:rFonts"))}
    assert fonts == {"標楷體"}


def test_form_scoped_checks_rows_and_blocks(tmp_path):
    make_blank(tmp_path / "b.docx")
    form = Form(str(tmp_path / "b.docx"))
    assert form.check("無任何需揭露")
    assert form.check("簡易審查", scope=form.row("1.申請型態"))
    r = form.row("(3)是否成年")
    assert form.check("否", scope=r, after="(4)")           # the second □否 only
    row = form.row("協同主持人", head=True)
    twin = form.clone_row(row)
    form.put("姓名", "王小明", scope=row)
    form.put("姓名", "李大華", scope=twin)
    form.delete_between("(附表一)", "(附表四)")
    assert not form.check("不存在的選項")
    form.save(str(tmp_path / "out.docx"))

    doc = Document(tmp_path / "out.docx")
    body = [p.text for p in doc.paragraphs]
    assert body[0] == "■無任何需揭露"
    assert "(附表一)" not in body and "試驗藥品簡介" not in body and "(附表四)" in body
    cells = [[c.text for c in r.cells] for r in doc.tables[0].rows]
    assert cells[0][1] == "□一般審查　■簡易審查"
    assert cells[1][1].startswith("姓名：王小明") and cells[2][1].startswith("姓名：李大華")
    assert cells[3][1] == "□是 □否 (4)是否健康 □是 ■否"
    assert form.missing == ["□不存在的選項"]
    # the inserted value is a run of its own in the form font
    run = next(r for r in doc.tables[0].rows[1].cells[1].paragraphs[0].runs if r.text.startswith("王小明"))
    assert run._r.find(f"{qn('w:rPr')}/{qn('w:rFonts')}").get(qn("w:eastAsia")) == "標楷體"


def test_set_cell_and_insert_paragraph(tmp_path):
    make_blank(tmp_path / "b.docx")
    form = Form(str(tmp_path / "b.docx"))
    assert form.cell("協同主持人", "第一行\n第二行")
    p = form.find_paragraph("試驗藥品簡介")
    new = form.insert_after(p, "補充說明")
    assert _ptext(new) == "補充說明" and new.getprevious() is p


def test_version_drift_and_rebuild_are_errors(tmp_path):
    make_blank(tmp_path / "b.docx")
    blank = Document(tmp_path / "b.docx")

    same = Document(tmp_path / "b.docx")
    rep = validate_layout.Report("same")
    validate_layout.check_version(same, blank, rep)
    validate_layout.check_labels(same, blank, rep)
    assert not rep.errors

    rebuilt = Document()
    rebuilt.add_paragraph("版次第11版　IRB.SF002　2025/03/03")
    rep = validate_layout.Report("rebuilt")
    validate_layout.check_version(rebuilt, blank, rep)
    validate_layout.check_labels(rebuilt, blank, rep)
    assert any("第11版" in e and "第12版" in e for e in rep.errors)
    assert any("涵蓋率" in e for e in rep.errors)


def test_glyph_lint_suggests_big5_replacements():
    rep = validate_layout.Report("x")
    validate_layout.check_glyphs("年齡≥20歲 ✓ 完成 ", rep)
    assert len(rep.warnings) == 1
    assert "≥→≧" in rep.warnings[0] and "✓→√" in rep.warnings[0]
