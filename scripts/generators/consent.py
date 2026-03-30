"""Consent / waiver / review-type form generators for KFSYSCC IRB.

Generates: SF003, SF004, SF005, SF062, SF063, SF075, SF090, SF091, SF092.
"""
import os

from scripts.docx_utils import (
    init_doc, set_cell_shading, add_p, add_ct, apply_tb,
    add_header, add_footer, check, set_run_font,
)
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Pt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _title_block(doc, subtitle):
    """Add standard two-line title block used by consent/review forms."""
    add_p(doc, "和信治癌中心醫院 人體試驗委員會",
          bold=True, size=16, alignment=WD_ALIGN_PARAGRAPH.CENTER, sa=Pt(0), sb=Pt(12))
    add_p(doc, subtitle,
          bold=True, size=14, alignment=WD_ALIGN_PARAGRAPH.CENTER, sa=Pt(0), sb=Pt(6))


def _signature_block(doc):
    """Add PI signature + date line."""
    add_p(doc, "")
    add_p(doc, "計畫主持人簽名：＿＿＿＿＿＿　日期：＿＿＿＿年＿＿月＿＿日",
          size=12, sa=Pt(0), sb=Pt(6))


def _save(doc, output_dir, filename):
    """Save document and return path."""
    path = os.path.join(output_dir, filename)
    doc.save(path)
    return path


# ---------------------------------------------------------------------------
# SF003 - 簡易審查範圍檢核表  v4, 2018/01/02
# ---------------------------------------------------------------------------

def generate_sf003(config, output_dir):
    """Generate SF003 expedited review scope checklist."""
    doc = init_doc()
    _title_block(doc, "簡易審查範圍檢核表")
    add_header(doc, config, inc_proj=True)

    add_p(doc, "本計畫符合下列簡易審查之範圍（請勾選）：", bold=True, size=12, sa=Pt(6), sb=Pt(6))

    is_retro = config["study"]["type"] == "retrospective"

    items = [
        (False, "1. 已核准之藥品或醫療器材，於新適應症或新用途之臨床試驗"),
        (False, "2. 利用無侵入性方式收集之生物檢體供研究用途"),
        (False, "3. 以非侵入性方式收集之臨床資料供研究用途"),
        (is_retro, "4. 既有資料、文件、紀錄或病理檢體之研究"),
        (False, "5. 聯邦政府或機構為研究、公共利益或公共服務計畫所收集之資料"),
        (False, "6. 食品之品質評估及消費者接受度之研究"),
        (False, "7. 其他經主管機關公告之研究"),
    ]

    for condition, text in items:
        add_p(doc, f"  {check(condition)} {text}", size=12, sa=Pt(2), sb=Pt(2))

    add_p(doc, "")
    add_p(doc, "備註說明：", bold=True, size=12, sa=Pt(6), sb=Pt(2))
    add_p(doc, "＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿", size=12, sa=Pt(2), sb=Pt(2))

    _signature_block(doc)
    add_footer(doc, "4", "IRB.SF003", "2018/01/02")

    return _save(doc, output_dir, "SF003_簡易審查範圍檢核表.docx")


# ---------------------------------------------------------------------------
# SF004 - 免予審查範圍檢核表  v2, 2016/11/07
# ---------------------------------------------------------------------------

def generate_sf004(config, output_dir):
    """Generate SF004 exempt review scope checklist."""
    doc = init_doc()
    _title_block(doc, "免予審查範圍檢核表")
    add_header(doc, config, inc_proj=True)

    add_p(doc, "本計畫符合下列免予審查之範圍（請勾選）：", bold=True, size=12, sa=Pt(6), sb=Pt(6))

    is_retro = config["study"]["type"] == "retrospective"

    items = [
        (False, "1. 於一般教學環境中進行之教育策略研究"),
        (False, "2. 教育測驗、訪談程序、問卷調查或公開行為觀察之研究"),
        (is_retro, "3. 利用既有之資料、文件、紀錄、病理檢體或診斷檢體之研究，且資料來源為公開或去識別化"),
        (False, "4. 公職人員或公職候選人之研究"),
        (False, "5. 食品之品質評估研究"),
        (False, "6. 其他"),
    ]

    for condition, text in items:
        add_p(doc, f"  {check(condition)} {text}", size=12, sa=Pt(2), sb=Pt(2))

    _signature_block(doc)
    add_footer(doc, "2", "IRB.SF004", "2016/11/07")

    return _save(doc, output_dir, "SF004_免予審查範圍檢核表.docx")


# ---------------------------------------------------------------------------
# SF005 - 免取得知情同意檢核表  v2, 2016/11/07
# ---------------------------------------------------------------------------

def generate_sf005(config, output_dir):
    """Generate SF005 waiver of consent checklist."""
    doc = init_doc()
    _title_block(doc, "免取得知情同意檢核表")
    add_header(doc, config, inc_proj=True)

    add_p(doc, "申請免取得受試者知情同意書之理由（請勾選符合之項目）：",
          bold=True, size=12, sa=Pt(6), sb=Pt(6))

    # All four criteria must be met for waiver to be valid
    items = [
        "1. 本研究對受試者所產生之風險不超過最低風險",
        "2. 免取得知情同意對受試者之權益不致產生不良影響",
        "3. 因研究設計之需要，無法事前取得受試者之知情同意",
        "4. 於適當情況下，受試者於研究參與後將會被提供額外之相關資訊",
    ]

    for text in items:
        add_p(doc, f"  {check(True)} {text}", size=12, sa=Pt(2), sb=Pt(2))

    # Explanation section
    data_period = config.get("dates", {}).get("data_period", "＿＿年至＿＿年間")
    explanation = (
        f"本研究為回溯性病歷審查研究，僅回顧分析{data_period}之"
        "既有去識別化病歷資料，不涉及任何介入性措施或直接接觸受試者。"
        "研究資料均已去識別化處理，無法連結至個別受試者。"
        "基於研究性質，事前取得每位受試者之知情同意實務上不可行且不必要。"
    )

    add_p(doc, "")
    add_p(doc, "說明：", bold=True, size=12, sa=Pt(6), sb=Pt(2))
    add_p(doc, explanation, size=12, sa=Pt(2), sb=Pt(2))

    _signature_block(doc)
    add_footer(doc, "2", "IRB.SF005", "2016/11/07")

    return _save(doc, output_dir, "SF005_免取得知情同意檢核表.docx")


# ---------------------------------------------------------------------------
# Consent form stubs: SF062, SF063, SF075, SF090, SF091, SF092
# ---------------------------------------------------------------------------

_CONSENT_STUB_META = {
    "SF062": ("受試者同意書（臨床研究）", "3", "IRB.SF062", "2018/07/09"),
    "SF063": ("受試者同意書（臨床試驗）", "3", "IRB.SF063", "2018/07/09"),
    "SF075": ("受試者同意書（基因研究）", "2", "IRB.SF075", "2017/06/05"),
    "SF090": ("受試者同意書（藥品試驗）", "2", "IRB.SF090", "2018/07/09"),
    "SF091": ("受試者同意書（兒童）", "2", "IRB.SF091", "2017/06/05"),
    "SF092": ("受試者同意書（醫療器材）", "2", "IRB.SF092", "2018/07/09"),
}


def _generate_consent_stub(config, output_dir, form_id):
    """Generate a consent form stub/template for the given form ID."""
    name_zh, ver, fno, date = _CONSENT_STUB_META[form_id]

    doc = init_doc()
    _title_block(doc, name_zh)
    add_header(doc, config, inc_proj=True)

    add_p(doc, "（本表單為範本，請依研究需求修改內容）",
          bold=True, size=12, alignment=WD_ALIGN_PARAGRAPH.CENTER, sa=Pt(6), sb=Pt(12))

    # Basic consent form structure with placeholders
    sections = [
        ("一、研究計畫說明", "（請說明本研究之目的、方法及預期效益）"),
        ("二、研究過程", "（請說明受試者參與之研究流程及持續時間）"),
        ("三、可能之風險與不適", "（請說明受試者可能面臨之風險、副作用或不適）"),
        ("四、預期之利益", "（請說明受試者及社會可能獲得之利益）"),
        ("五、替代方案", "（請說明不參與本研究時可選擇之其他治療或處置方式）"),
        ("六、保密性", "（請說明受試者個人資料之保密措施）"),
        ("七、補償與賠償", "（請說明受試者因參與研究所受傷害之補償與賠償機制）"),
        ("八、自願參與及退出", "（請說明受試者有權自願參與及隨時退出，且不影響其醫療權益）"),
        ("九、聯絡方式", "（請提供受試者可諮詢之聯絡人及電話）"),
    ]

    for title, placeholder in sections:
        add_p(doc, title, bold=True, size=12, sa=Pt(8), sb=Pt(2))
        add_p(doc, placeholder, size=12, sa=Pt(2), sb=Pt(2))

    # Signature area
    add_p(doc, "")
    add_p(doc, "受試者同意聲明", bold=True, size=12, sa=Pt(8), sb=Pt(4))
    add_p(doc, "本人已詳閱以上說明，並有機會詢問相關問題，本人同意參加本研究。",
          size=12, sa=Pt(2), sb=Pt(6))
    add_p(doc, "受試者簽名：＿＿＿＿＿＿　日期：＿＿＿＿年＿＿月＿＿日",
          size=12, sa=Pt(2), sb=Pt(2))
    add_p(doc, "法定代理人簽名：＿＿＿＿＿＿　日期：＿＿＿＿年＿＿月＿＿日",
          size=12, sa=Pt(2), sb=Pt(2))
    add_p(doc, "見證人簽名：＿＿＿＿＿＿　日期：＿＿＿＿年＿＿月＿＿日",
          size=12, sa=Pt(2), sb=Pt(2))
    add_p(doc, "計畫主持人/協同主持人簽名：＿＿＿＿＿＿　日期：＿＿＿＿年＿＿月＿＿日",
          size=12, sa=Pt(2), sb=Pt(2))

    add_footer(doc, ver, fno, date)

    filename = f"{form_id}_{name_zh}.docx"
    return _save(doc, output_dir, filename)


def generate_sf062(config, output_dir):
    """Generate SF062 consent form stub (clinical research)."""
    return _generate_consent_stub(config, output_dir, "SF062")


def generate_sf063(config, output_dir):
    """Generate SF063 consent form stub (clinical trial)."""
    return _generate_consent_stub(config, output_dir, "SF063")


def generate_sf075(config, output_dir):
    """Generate SF075 consent form stub (genetic research)."""
    return _generate_consent_stub(config, output_dir, "SF075")


def generate_sf090(config, output_dir):
    """Generate SF090 consent form stub (drug trial)."""
    return _generate_consent_stub(config, output_dir, "SF090")


def generate_sf091(config, output_dir):
    """Generate SF091 consent form stub (children)."""
    return _generate_consent_stub(config, output_dir, "SF091")


def generate_sf092(config, output_dir):
    """Generate SF092 consent form stub (medical device)."""
    return _generate_consent_stub(config, output_dir, "SF092")


# ---------------------------------------------------------------------------
# ALL_GENERATORS registry
# ---------------------------------------------------------------------------

ALL_GENERATORS = {
    "SF003": generate_sf003,
    "SF004": generate_sf004,
    "SF005": generate_sf005,
    "SF062": generate_sf062,
    "SF063": generate_sf063,
    "SF075": generate_sf075,
    "SF090": generate_sf090,
    "SF091": generate_sf091,
    "SF092": generate_sf092,
}
