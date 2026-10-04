"""Shared DOCX helper functions for IRB form generation.

Extracted from irb-close/generate_forms.py, refactored to accept config dict.
"""
import os
import yaml
from docx import Document
from docx.shared import Pt, Cm, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

from scripts.institution import current


def load_config(path="config.yml"):
    """Load and return config dict from YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def check(condition: bool) -> str:
    """Return ■ if True, □ if False (IRB checkbox convention)."""
    return "■" if condition else "□"


# Page setup + per-form margins come from the institution profile, copied from
# the official blanks' sectPr. (python-docx's default template is US Letter
# with 3.17 cm sides, which shifts every line break and table width.)
def institution():
    """Active institution profile (name, committee, labels, page, font)."""
    return current()


def _page_setup():
    pg = current().page
    m = pg["margins"]
    return {
        "page_width": Twips(pg["width"]), "page_height": Twips(pg["height"]),
        "left_margin": Twips(m["left"]), "right_margin": Twips(m["right"]),
        "top_margin": Twips(m["top"]), "bottom_margin": Twips(m["bottom"]),
        "header_distance": Twips(pg.get("header_distance", 851)),
        "footer_distance": Twips(pg.get("footer_distance", 992)),
    }


def form_id_from_path(path):
    """'SF002_KF-001.docx' → 'SF002'; '中文計畫摘要_proposal.docx' → 'PROPOSAL'."""
    return current().form_id(os.path.basename(path))


def official_margins(form_id):
    """(left, right, top, bottom) in twips of the official blank form."""
    pg = current().page
    if form_id in pg.get("per_form_margins", {}):
        return tuple(pg["per_form_margins"][form_id])
    m = pg["margins"]
    return (m["left"], m["right"], m["top"], m["bottom"])


def apply_official_page_setup(path):
    """Re-save a generated DOCX with A4 + the official margins of its form."""
    doc = Document(path)
    left, right, top, bottom = official_margins(form_id_from_path(path))
    setup = _page_setup()
    for section in doc.sections:
        section.page_width, section.page_height = setup["page_width"], setup["page_height"]
        section.left_margin, section.right_margin = Twips(left), Twips(right)
        section.top_margin, section.bottom_margin = Twips(top), Twips(bottom)
    doc.save(path)


# fontTable entries Word itself writes, for fonts we know. altName lets Word
# resolve the font by its English name (標楷體 → DFKai-SB on Windows; macOS
# ships it as BiauKai with the same localized name). Other fonts get a minimal
# entry with the profile's first alias as altName.
_KNOWN_FONT_ENTRIES = {"標楷體": (
    '<w:font w:name="標楷體"><w:altName w:val="DFKai-SB"/>'
    '<w:panose1 w:val="03000509000000000000"/><w:charset w:val="88"/>'
    '<w:family w:val="script"/><w:pitch w:val="fixed"/>'
    '<w:sig w:usb0="00000003" w:usb1="080E0000" w:usb2="00000016" w:usb3="00000000"'
    ' w:csb0="00100001" w:csb1="00000000"/></w:font>'
)}


def form_font():
    return current().font["name"]


def _font_table_entry():
    font = current().font
    if font["name"] in _KNOWN_FONT_ENTRIES:
        return _KNOWN_FONT_ENTRIES[font["name"]]
    alt = font.get("aliases", [])
    alt_xml = f'<w:altName w:val="{alt[0]}"/>' if alt else ""
    return f'<w:font w:name="{font["name"]}">{alt_xml}</w:font>'


def _apply_cross_platform_defaults(doc):
    """Pin page setup, fonts and language so Word (Win/Mac) and LibreOffice agree."""
    for section in doc.sections:
        for attr, value in _page_setup().items():
            setattr(section, attr, value)
    pin_form_font(doc)


def _child(parent, tag, first=False):
    """Find or create a child element (first=True inserts it at the front)."""
    el = parent.find(qn(tag))
    if el is None:
        el = parse_xml(f'<{tag} {nsdecls("w")}/>')
        parent.insert(0, el) if first else parent.append(el)
    return el


def pin_form_font(doc):
    """Make the profile's form font the document default (+ fontTable entry)."""
    # docDefaults: replace theme fonts (which resolve to Calibri/MS 明朝 on an
    # en-US theme) with the explicit form font, and tag the form language.
    font = form_font()
    styles = doc.styles.element
    rpr_default = _child(_child(_child(styles, 'w:docDefaults', first=True), 'w:rPrDefault'), 'w:rPr')
    fonts = _child(rpr_default, 'w:rFonts', first=True)
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        fonts.set(qn(a), font)
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        fonts.attrib.pop(qn(a), None)
    _child(rpr_default, 'w:lang').set(qn('w:eastAsia'), current().font.get('lang', 'zh-TW'))

    for part in doc.part.package.iter_parts():
        if str(part.partname) == '/word/fontTable.xml' and font.encode() not in part.blob:
            part._blob = part.blob.replace(
                b'</w:fonts>', _font_table_entry().encode('utf-8') + b'</w:fonts>')


def strip_theme_fonts(doc):
    """Resolve theme font references in styles and runs to the form font.

    Official blanks often carry them; they override docDefaults and resolve
    differently per OS/locale."""
    font = form_font()
    for root in (doc.styles.element, doc.element.body):
        for rf in root.iter(qn('w:rFonts')):
            for theme, plain in (('w:asciiTheme', 'w:ascii'), ('w:hAnsiTheme', 'w:hAnsi'),
                                 ('w:eastAsiaTheme', 'w:eastAsia'), ('w:cstheme', 'w:cs')):
                if rf.attrib.pop(qn(theme), None) is not None:
                    rf.set(qn(plain), font)


def init_doc(sz=12):
    """Create a new Document with the institution's page setup and form font."""
    doc = Document()
    _apply_cross_platform_defaults(doc)
    s = doc.styles['Normal']
    s.font.name = form_font()
    s.font.size = Pt(sz)
    s.element.rPr.rFonts.set(qn('w:eastAsia'), form_font())
    return doc


def set_cell_shading(cell, color):
    """Set cell background color."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}" w:val="clear"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_border(cell, **kwargs):
    """Set cell borders. kwargs: top, bottom, start, end with {val, sz, color}."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}></w:tcBorders>')
    for edge, attrs in kwargs.items():
        element = parse_xml(
            f'<w:{edge} {nsdecls("w")} w:val="{attrs.get("val", "single")}" '
            f'w:sz="{attrs.get("sz", 4)}" w:space="0" '
            f'w:color="{attrs.get("color", "000000")}"/>'
        )
        tcBorders.append(element)
    tcPr.append(tcBorders)


def set_run_font(run, font_name=None, size=12, bold=False):
    """Set run font (default: institution form font) with eastAsia fallback."""
    font_name = font_name or form_font()
    run.font.name = font_name
    run.font.size = Pt(size)
    run.bold = bold
    rPr = run.font.element.rPr
    if rPr is None:
        run.font.element.get_or_add_rPr()
        rPr = run.font.element.rPr
    rPr.rFonts.set(qn('w:eastAsia'), font_name)


def add_p(doc, text, bold=False, size=12, alignment=None, sa=Pt(6), sb=Pt(0)):
    """Add a formatted paragraph to the document."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, None, size, bold)
    if alignment:
        p.alignment = alignment
    p.paragraph_format.space_after = sa
    p.paragraph_format.space_before = sb
    return p


def add_ct(cell, text, bold=False, size=10, alignment=None):
    """Add formatted text to a table cell."""
    p = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()
    p.clear()
    run = p.add_run(text)
    set_run_font(run, None, size, bold)
    if alignment:
        p.alignment = alignment
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    return p


def apply_tb(tbl):
    """Apply borders to all cells in a table."""
    for row in tbl.rows:
        for cell in row.cells:
            set_cell_border(
                cell,
                top={"sz": 4}, bottom={"sz": 4},
                start={"sz": 4}, end={"sz": 4},
            )


def add_header(doc, config, inc_proj=True):
    """Add standard IRB header block (IRB no, title, PI, dept)."""
    rows = 5 if inc_proj else 4
    tbl = doc.add_table(rows=rows, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    i = 0
    add_ct(tbl.rows[i].cells[0], current().irb_no_label, True, 11)
    add_ct(tbl.rows[i].cells[1], config["study"]["irb_no"], size=11)

    if inc_proj:
        i += 1
        add_ct(tbl.rows[i].cells[0], "計畫編號", True, 11)
        add_ct(tbl.rows[i].cells[1], config["study"].get("project_no", "不適用"), size=11)

    i += 1
    add_ct(tbl.rows[i].cells[0], "計畫名稱", True, 11)
    cell = tbl.rows[i].cells[1]
    p = cell.paragraphs[0]
    p.clear()
    run = p.add_run(f"（中文）{config['study']['title_zh']}")
    set_run_font(run, size=10)
    p.paragraph_format.space_after = Pt(2)
    p2 = cell.add_paragraph()
    run2 = p2.add_run(f"（英文）{config['study']['title_en']}")
    set_run_font(run2, size=10)
    p2.paragraph_format.space_after = Pt(2)

    i += 1
    # Build PI/co-PI string
    pi_str = config["pi"]["name"]
    co_pis = config.get("co_pi", [])
    if co_pis:
        pi_str += "（主持人）"
        for cp in co_pis:
            pi_str += f"\n{cp['name']}（共同主持人）"
    add_ct(tbl.rows[i].cells[0], "計畫主持人", True, 11)
    add_ct(tbl.rows[i].cells[1], pi_str, size=11)

    i += 1
    add_ct(tbl.rows[i].cells[0], "單位／職稱", True, 11)
    add_ct(tbl.rows[i].cells[1], config["pi"]["dept"], size=11)

    apply_tb(tbl)
    doc.add_paragraph()


def add_footer(doc, ver, fno, date):
    """Add version/form number footer."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(f"版次第{ver}版　{fno}　{date}")
    set_run_font(run, size=9)
