"""Generate 中文計畫摘要 (Chinese Project Summary) (KFSYSCC form pack).

Required for new case submission. Max 2 pages.
11 sections per KFSYSCC official template.
"""
import os
import re

from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from irb_in_hurry.docx_utils import (
    add_ct,
    add_p,
    apply_tb,
    form_filename,
    init_doc,
    institution,
)


def _study_type_zh(config):
    """Get Chinese description of study type."""
    t = config["study"].get("type", "")
    d = config["study"].get("design", "")
    mapping = {
        "retrospective": "回溯性",
        "prospective": "前瞻性",
        "clinical_trial": "臨床試驗",
        "genetic": "基因研究",
    }
    design_mapping = {
        "cohort": "世代研究",
        "case_control": "病例對照研究",
        "cross_sectional": "橫斷面研究",
        "rct": "隨機對照試驗",
        "single_arm": "單臂研究",
    }
    type_zh = mapping.get(t, t)
    design_zh = design_mapping.get(d, d)
    return f"{type_zh}{design_zh}"


def _text(prop, key, placeholder):
    """Free-text proposal section → str (lists become `1. …` lines)."""
    v = prop.get(key)
    if isinstance(v, list):
        return "\n".join(f"{i}. {x}" for i, x in enumerate(v, 1))
    # Wrapped source lines leave spaces; drop them next to CJK, keep newlines
    v = re.sub(r"[^\S\n]*([\u3000-\u303f\u4e00-\u9fff\uff00-\uffef])[^\S\n]*", r"\1",
               (v or "").strip())
    return v or placeholder


# The official blank's 11 headings, in order (also the rebuild's section titles).
SECTION_TITLES = [
    "研究主題", "研究背景", "研究目的", "研究執行期限", "研究設計", "研究參與者",
    "研究方法", "副作用處理", "統計分析", "研究參與者資料保護措施及安全監測計畫", "附錄",
]


def summary_sections(config):
    """[(official heading, text)] for the 11 sections of the 中文計畫摘要.

    Shared by the rebuild below and the official-blank filler
    (institutions/kfsyscc/fill.py), so both say the same thing."""
    is_retro = config["study"].get("type") == "retrospective"
    study_type_zh = _study_type_zh(config)
    data_period = config["dates"].get("data_period", "")
    planned_n = config["subjects"].get("planned_n", 0)
    # Optional free-text content; each section falls back to the placeholder
    prop = config.get("proposal") or {}
    if not isinstance(prop, dict):
        prop = {}

    def t(key, placeholder):
        return _text(prop, key, placeholder)

    period = f"自{config['dates'].get('study_start', '')}至{config['dates'].get('study_end', '')}"
    if is_retro and data_period:
        period += f"\n資料回溯期間：{data_period}"

    design = f"本研究採{study_type_zh}設計"
    if is_retro:
        design += f"，回溯分析{data_period}期間之病歷資料。"
        design += "\n本研究為非介入性研究，不涉及任何實驗性處置。"
    else:
        design += "。\n（請說明對照組、盲性、隨機分組等設計。）"
    if prop.get("design"):
        design += "\n" + t("design", "")

    subj = f"預計收錄人數：{planned_n}人"
    groups = config["subjects"].get("groups", [])
    if groups:
        subj += "\n分組："
        for g in groups:
            subj += f"\n  - {g['name']}"
            if g.get("n"):
                subj += f"：{g['n']}人"
    for label, key in (("納入條件", "inclusion"), ("排除條件", "exclusion")):
        items = t(key, "（請列出）")
        subj += f"\n{label}：" + ("\n" if "\n" in items else "") + items
    if config["subjects"].get("consent_waiver"):
        subj += "\n研究參與者權益：本研究為回溯性病歷審查，申請免取得知情同意，所有資料均去識別化處理。"
    else:
        subj += "\n研究參與者權益：（請說明知情同意取得方式及受試者保護機制。）"

    if is_retro:
        methods = (f"資料來源：{institution().ehr_name}\n"
                   "資料收集項目：" + t("variables", "（請列出收集之臨床變項）") + "\n"
                   "研究終點：" + t("endpoints", "（請列出主要及次要研究終點）"))
        if prop.get("methods"):
            methods += "\n" + t("methods", "")
    else:
        methods = t("methods", "（請說明治療程序、劑量、臨床觀察、追蹤時程及療效評估。）")

    if prop.get("adverse_events"):
        adverse = t("adverse_events", "")
    elif is_retro:
        adverse = "不適用。本研究為回溯性病歷審查研究，非介入性研究，無不良事件通報需求。"
    else:
        adverse = "（請說明不良事件的發生率及處理原則。）"

    ds = config.get("closure", {}).get("data_safety", {})
    safety = []
    if ds.get("deidentified"):
        safety.append("所有資料均去識別化處理")
    if ds.get("encrypted"):
        safety.append("電子資料以加密方式儲存，設有密碼保護")
    if ds.get("retention_years"):
        safety.append(f"資料保存期限：研究結束後{ds['retention_years']}年")
    if ds.get("authorized_personnel"):
        safety.append(f"資料存取授權人員：{ds['authorized_personnel']}")
    protection = t("data_protection", "") or "\n".join(safety) or \
        "（請說明資料保密措施及受試者安全監測計畫。）"

    return list(zip(SECTION_TITLES, [
        config["study"]["title_zh"] + (f"\n{config['study']['title_en']}"
                                       if config["study"].get("title_en") else ""),
        t("background", "（請簡述疾病現況、自然病程、現有治療方式及預後，說明本研究之必要性。）"),
        t("objectives", "（請說明主要研究目的及次要研究目的。）"),
        period,
        design,
        subj,
        methods,
        adverse,
        t("statistics", "（請說明統計分析計畫，包含期中分析（如適用）。）"),
        protection,
        t("attachments", "（如有相關附件，請列出。）"),
    ], strict=True))


NUMERALS = "一二三四五六七八九十"


def generate_proposal_summary(config, output_dir):
    """Rebuild 中文計畫摘要 (used when the official blank isn't cached). Max 2 pages."""
    doc = init_doc(11)

    # Title
    add_p(doc, institution().heading, True, 13,
          WD_ALIGN_PARAGRAPH.CENTER, Pt(2))
    add_p(doc, "中文計畫摘要", True, 15,
          WD_ALIGN_PARAGRAPH.CENTER, Pt(8))

    # Header info table
    tbl = doc.add_table(rows=3, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_ct(tbl.rows[0].cells[0], institution().irb_no_label, True, 10)
    add_ct(tbl.rows[0].cells[1], config["study"]["irb_no"] or "（待核發）", size=10)
    add_ct(tbl.rows[1].cells[0], "計畫名稱", True, 10)
    add_ct(tbl.rows[1].cells[1], config["study"]["title_zh"], size=10)
    add_ct(tbl.rows[2].cells[0], "計畫主持人", True, 10)
    pi_str = config["pi"]["name"]
    co_pis = config.get("co_pi", [])
    if co_pis:
        pi_str += "（主持人）、" + "、".join(
            f"{cp['name']}（共同主持人）" for cp in co_pis
        )
    add_ct(tbl.rows[2].cells[1], pi_str, size=10)
    apply_tb(tbl)

    doc.add_paragraph()

    for i, (title, text) in enumerate(summary_sections(config)):
        num = NUMERALS[i] if i < 10 else "十" + NUMERALS[i - 10]
        add_p(doc, f"{num}、{title}", True, 11, sa=Pt(4), sb=Pt(4))
        add_p(doc, text, size=10, sa=Pt(2))

    # Footer note
    doc.add_paragraph()
    add_p(doc, "※ 本摘要以不超過2頁為原則。", size=9,
          alignment=WD_ALIGN_PARAGRAPH.RIGHT, sa=Pt(2))

    path = os.path.join(output_dir, form_filename("中文計畫摘要", config, "待核發"))
    doc.save(path)
    return path


ALL_GENERATORS = {
    "PROPOSAL": generate_proposal_summary,
}
