"""KFSYSCC new-case forms filled into the official blanks (templates/kfsyscc/).

Each generator copies the cached official blank and fills it in place, so the
output keeps the official header (版次/編修日期/文件標號), every option, the
instructions and the reviewer-only sections. Without a cached blank
(`irbh templates` not run, e.g. in CI) it falls back to the python-docx rebuild
in `irb_in_hurry.generators.*` and says so; the layout gate then flags that
output as a rebuild (low official-text coverage, version drift).

Anchors are the blanks' own wording (KFSYSCC SF002 v12, SF001 v9, SF003 v4,
SF004, SF005, SF094 v1, 中文計畫摘要). A label the blank no longer has is
reported after generation, which is the cue that KFSYSCC revised the form.
"""
import copy
import datetime
import os
import re

from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Pt
from docx.text.run import Run

from irb_in_hurry.docx_utils import form_filename, form_font
from irb_in_hurry.generators import consent, new_case, proposal
from irb_in_hurry.template_fill import Form, _ptext, blank_path_or_none

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _blank_or_rebuild(form_id, rebuild):
    """Decorator: fill the official blank, or fall back to the rebuild generator."""
    def wrap(fill):
        def generate(config, output_dir):
            blank = blank_path_or_none(form_id)
            if blank is None:
                print(f"    ⚠ {form_id}: no official blank cached — rebuilt layout "
                      f"(run `irbh templates` to fill the official form instead)")
                return rebuild(config, output_dir)
            return fill(Form(blank), config, output_dir)
        generate.__name__ = fill.__name__
        generate.__doc__ = fill.__doc__
        return generate
    return wrap


def _finish(form, form_id, config, output_dir, fallback, name=None):
    fname = form_filename(form_id, config, fallback)
    if name:
        fname = fname[:-5] + f"_{name}.docx"
    path = os.path.join(output_dir, fname)
    form.save(path)
    if form.missing:
        print(f"    ⚠ {form_id}: not found in the official blank (revised form?): "
              + "、".join(form.missing))
    return path


def _team(config):
    """[(role, person)] — role ∈ pi / co_pi / staff."""
    team = [("pi", config["pi"])]
    team += [("co_pi", p) for p in config.get("co_pi") or []]
    team += [("staff", p) for p in config.get("staff") or []]
    return team


def _irb_no(config):
    return config["study"].get("irb_no") or ""


def _is_retro(config):
    return config["study"].get("type") == "retrospective"


def _period(text):
    """'2013年01月01日 至 2023年12月31日' → ('2013年01月01日', '2023年12月31日')."""
    parts = re.split(r"\s*(?:至|~|～|–|-)\s*", text or "", maxsplit=1)
    return (parts[0], parts[1]) if len(parts) == 2 else (text or "", "")


def _funding(config):
    return config["study"].get("funding") or "不需補助"


def _header_cells(form, config, irb_label="KFSYSCC-IRB編號"):
    """The 編號 / 計畫名稱 / 主持人 block shared by SF001, SF022 and SF094."""
    study, pi = config["study"], config["pi"]
    form.cell(irb_label, _irb_no(config))
    form.cell("計畫編號", study.get("project_no") or "不適用")
    form.cell("中文", study["title_zh"])
    form.cell("英文", study.get("title_en", ""))
    form.cell("計畫主持人", pi["name"])
    form.cell("單位/職稱", pi.get("dept", ""))


# ---------------------------------------------------------------------------
# SF001 — 新案審查送審資料表及文件繳交完成簽收表
# ---------------------------------------------------------------------------

def _sf001_items(config):
    """Checklist item number → needed for this study."""
    study, subj = config["study"], config["subjects"]
    drug = study.get("drug_device")
    attachments = str((config.get("proposal") or {}).get("attachments", "")) \
        if isinstance(config.get("proposal"), dict) else ""
    crf = drug or any(k in attachments for k in ("Case Report", "個案報告", "資料收集表"))
    return {
        1: True, 2: True, 3: study["review_type"] == "expedited",
        4: study["review_type"] == "exempt", 5: True, 6: True, 7: True,
        8: not subj.get("consent_waiver"), 9: bool(subj.get("consent_waiver")),
        10: bool(study.get("questionnaire")), 11: crf, 12: drug, 13: drug,
        14: True, 15: True, 16: drug, 17: drug,
        18: study["review_type"] == "full_board", 19: False, 20: True,
    }


@_blank_or_rebuild("SF001", new_case.generate_sf001)
def generate_sf001(form, config, output_dir):
    """SF001 送審資料表: header + √ for every document this study submits."""
    study, subj = config["study"], config["subjects"]
    _header_cells(form, config)

    table = form.table("資料項目")
    for tr in table.findall(qn("w:tr")) if table is not None else []:
        tcs = tr.findall(qn("w:tc"))
        if len(tcs) < 4:
            continue
        item = re.sub(r"\s", "", "".join(t.text or "" for t in tcs[3].iter(qn("w:t"))))
        m = re.match(r"(\d+)\.", item)
        if m and _sf001_items(config).get(int(m.group(1))):
            form.set_cell(tcs[0], "√")      # 備妥請打√ (√ is in 標楷體; ✓ is not)

    row = form.row("試驗計畫書", head=False)
    if _is_retro(config):
        form.check("病歷回溯研究", scope=row)
    elif study["type"] == "clinical_trial":
        form.check("臨床試驗計畫書", scope=row)
    else:
        form.check("臨床研究計畫書", scope=row)

    if not subj.get("consent_waiver"):
        row = form.row("『受試者同意書』格式")
        if study.get("drug_device"):
            form.check("藥品臨床試驗受試者同意書", scope=row)
        else:
            form.check("受試者同意書", scope=row)
        if study.get("genetic"):
            form.check("基因研究受試者同意書", scope=row)
        if subj.get("vulnerable_population"):
            form.check("兒童版受試者同意書", scope=row)
    return _finish(form, "SF001", config, output_dir, "新案審查送審資料表")


# ---------------------------------------------------------------------------
# SF002 — 研究計畫申請書 (v12, 2026/03/02)
# ---------------------------------------------------------------------------

def _person(form, row, person):
    form.put("姓名", person.get("name", ""), scope=row)
    form.put("服務機構/單位/職稱", person.get("dept", ""), scope=row)
    if person.get("phone"):
        form.put("連絡電話", person["phone"], scope=row)
    if person.get("email"):
        form.put("e-mail", person["email"], scope=row)
    if person.get("training_hours") not in (None, ""):
        form.put("近6年內共", person["training_hours"], scope=row)


def _people_rows(form, anchor, people):
    """Fill one row per person (cloning the official row); drop it when empty."""
    row = form.row(anchor, head=True)
    if row is None:
        return
    if not people:
        form.delete_row(row)
        return
    pristine = copy.deepcopy(row)
    last = row
    for i, person in enumerate(people):
        if i:
            new = copy.deepcopy(pristine)
            last.addnext(new)
            last = new
        _person(form, last, person)


@_blank_or_rebuild("SF002", new_case.generate_sf002)
def generate_sf002(form, config, output_dir):
    """SF002 研究計畫申請書 (official blank, every option kept)."""
    study, subj, dates, pi = config["study"], config["subjects"], config["dates"], config["pi"]
    retro, drug, waiver = _is_retro(config), study.get("drug_device"), subj.get("consent_waiver")
    ck, row = form.check, form.row

    r = row("計畫名稱", head=True)
    form.put("中文", study["title_zh"], scope=r)
    form.put("英文", study.get("title_en", ""), scope=r)

    # 總主持人／指導老師 rows: only for cooperative / graduate-student projects
    supervisor = config.get("supervisor")
    if supervisor:
        r = row("總主持人(合作計畫)", head=True)
        ck(supervisor.get("role", "總主持人"), scope=r)
        _person(form, r, supervisor)
    else:
        form.delete_row(row("總主持人或指導老師於本院", head=True))
        form.delete_row(row("總主持人(合作計畫)", head=True))

    r = row("院內計畫主持人(合作計畫)", head=True)
    ck("計畫主持人", scope=r)
    _person(form, r, pi)
    _people_rows(form, "協同主持人", config.get("co_pi") or [])
    _people_rows(form, "研究人員", config.get("staff") or [])

    contact = config.get("contact") or pi
    r = row("聯絡人", head=True)
    ck("院內", scope=r)
    form.put("姓名", contact.get("name", ""), scope=r)
    form.put("連絡電話/分機", contact.get("phone", ""), scope=r)
    if contact.get("email"):
        form.put("e-mail", contact["email"], scope=r)

    # 研究基本資料
    r = row("1.申請型態")
    ck({"full_board": "一般審查", "expedited": "簡易審查",
        "exempt": "免予審查"}[study["review_type"]], scope=r)
    r = row("2.執行中心類型")
    ck("本國多中心" if study.get("multicenter") else "本院", scope=r)
    r = row("3.計畫類型")
    if study.get("genetic"):
        ck("基因相關臨床試驗", scope=r)
    if not drug:
        ck("一般學術研究", scope=r)
    ck("是" if drug else "否", scope=r, after="是否須經中央主管機關核准")
    r = row("4.研究/試驗計畫簡介")
    if drug:
        ck("試驗藥品/疫苗", scope=r)
    if study.get("genetic"):
        ck("基因研究", scope=r)
    if not drug:
        ck("觀察性/回溯性/其他研究", scope=r)
    ck("計畫主持人", scope=row("5.研究計畫起始於"))
    ck(_funding(config), scope=row("6.請列出此研究計畫"))
    ck("本院/計畫主持人", scope=row("7.研究計畫責任歸屬"))

    # 研究類別與設計
    form.sub(r"自公元.*?日[ \t　]*至公元.*日",
             f"自公元{dates['study_start']} 至公元{dates['study_end']}",
             scope=row("8.預期研究"))
    if not drug:
        ck("不適用", scope=row("9.試驗產品"))
    r = row("10.收案/招募")
    if retro:
        ck("病歷回溯研究", scope=r)
        a, b = _period(dates.get("data_period"))
        form.sub(r"(病歷回溯研究[:：]申請年份為)公元.*?日至公元.*?日", rf"\1公元{a}至公元{b}", scope=r)
    else:
        ck("計畫主持人(含共/協同主持人)口頭介紹", scope=r)
    ck("不適用" if retro else "否", scope=row("11.競爭性收案"))

    r = row("12.研究模式")
    if study["type"] == "clinical_trial":
        ck("介入性研究", scope=r)
    else:
        ck("非介入研究", scope=r)
        model = {"cohort": "世代研究", "case_control": "病例對照研究",
                 "case_series": "病例研究"}.get(study.get("design"))
        if model:
            ck(model, scope=r)
        collect = "回溯性" if retro else {"cross_sectional": "橫斷性"}.get(study.get("design"), "前瞻性")
        ck(collect, scope=r, after="(2)資料收集")
    ck("不適用" if retro else "否", scope=row("13.研究參與者是否會被取消"))
    r = row("14.資料及安全性監測")
    ck("有" if study["review_type"] == "full_board" else "無", scope=r, after="監測計畫")
    ck("無", scope=r, after="之設置")
    r = row("15.資料保密方式")
    ds = config.get("closure", {}).get("data_safety", {})
    if ds.get("deidentified", True):
        ck("以編號辨識", scope=r)
        ck("將資料編碼", scope=r)
    if ds.get("encrypted"):
        ck("編號或編碼之資料上鎖", scope=r)
    ck("不適用" if not drug else "無", scope=row("16.研究計畫是否有試驗保單"))

    # 受試者資料
    r = row("17.收案人數")
    form.sub(r"本院[ \t　]+人", f"本院 {subj['planned_n']} 人", scope=r)
    if not study.get("multicenter"):
        form.sub(r"國內[ \t　]+人", f"國內 {subj['planned_n']} 人", scope=r)
    r = row("18.受試者特徵")
    if subj.get("population"):
        form.put("受試者型態（如：健康人、罹患特殊疾病之病患）", subj["population"], scope=r)
    if subj.get("age_range"):
        lo, _, hi = str(subj["age_range"]).partition("-")
        form.sub(r"[ \t　]+歲至[ \t　]+歲", f" {lo} 歲至 {hi or '　'} 歲", scope=r)
    if retro:
        ck("不適用", scope=r, after="(3)本研究計畫是否僅收納")
        ck("不適用", scope=r, after="(5)是否如研究計畫")
    ck("否", scope=r, after="(6)本研究計畫將納入健康受試者")
    ck("否", scope=r, after="(7)受試者含胎兒或屍體")
    ck("否", scope=r, after="(8)受試者與研究計畫主持人")
    r = row("19.收案對象是否納入易受傷害團體")
    ck("是" if subj.get("vulnerable_population") else "否", scope=r)
    r = row("20.使用輻射物質")
    if not drug:
        ck("否", scope=r, after="將接受輻射暴露")
        ck("否", scope=r, after="(4)是否利用輻射化學物質")
    ck("無", scope=row("21.使用生物感染源"))
    if not config.get("closure", {}).get("specimens"):
        ck("不需檢體", scope=row("22.研究用之檢體"))

    # 招募方式與知情同意程序
    ck("不適用" if retro else "無", scope=row("24.支付受試者酬金"))
    ck("免簽署受試者同意書" if waiver else "檢附受試者同意書", scope=row("25.是否簽署受試者同意書"))
    r = row("32.受試者/研究對象之風險")
    ck("參加本計畫將面臨的風險與未參加計畫時相當", scope=r)
    ck("參加本計畫時，其權益與未參加計畫時相當", scope=r)

    # 附表: keep only the ones this study needs (一～三 drug/device/technique, 四 genetic)
    if not drug:
        form.delete_between("(附表一)", "(附表四)")
    if not study.get("genetic"):
        form.delete_between("(附表四)")
    if not drug and not study.get("genetic"):
        form.delete_between("請檢附附表，不適用之表格請自行抽掉", "(附表")
    return _finish(form, "SF002", config, output_dir, "研究計畫申請書")


# ---------------------------------------------------------------------------
# SF003 / SF004 — 簡易 / 免予審查範圍檢核表
# ---------------------------------------------------------------------------

def _scope_header(form, config):
    form.cell("KFSYSCC-IRB編號", _irb_no(config))
    form.cell("計畫主持人", config["pi"]["name"])
    title = config["study"]["title_zh"]
    # the title cell is half the page wide: long titles in 10 pt keep the form on its pages
    form.cell("計畫名稱", title, size=10 if len(title) > 40 else None)


@_blank_or_rebuild("SF003", consent.generate_sf003)
def generate_sf003(form, config, output_dir):
    """SF003 簡易審查範圍檢核表."""
    _scope_header(form, config)
    if _is_retro(config):
        form.check("使用臨床常規治療或診斷之資料")
    if config["study"].get("genetic"):
        form.check("基因研究")
    if config["study"]["type"] == "clinical_trial":
        form.check("隨機分組設計")
    return _finish(form, "SF003", config, output_dir, "簡易審查範圍檢核表")


@_blank_or_rebuild("SF004", consent.generate_sf004)
def generate_sf004(form, config, output_dir):
    """SF004 免予審查範圍檢核表."""
    _scope_header(form, config)
    if _is_retro(config):
        form.check("研究計畫屬最低風險")
    return _finish(form, "SF004", config, output_dir, "免予審查範圍檢核表")


# ---------------------------------------------------------------------------
# SF005 — 免取得知情同意檢核表
# ---------------------------------------------------------------------------

SF005_CRITERIA = {          # 自評項目 → anchor in its row
    1: "公務機關執行法定職務",
    2: "自合法之生物資料庫取得",
    3: "且免除事先取得同意並不影響",
    4: "不免除事先取得研究對象同意則無法進行",
}


def _waiver_reason(config):
    subj = config["subjects"]
    if subj.get("waiver_reason"):
        return subj["waiver_reason"]
    period = config["dates"].get("data_period") or "既定期間"
    return (f"本研究為回溯性病歷審查研究，僅回顧分析{period}之既有病歷資料，"
            "所有個案均屬例行性醫療，資料於計畫提出前已完成，不涉及任何介入性措施或直接接觸研究對象；"
            "資料以編碼去識別化處理，研究屬最低風險。研究對象多已失聯或死亡，"
            "若須逐一取得同意則研究無法進行，免除同意並不影響研究對象之權益。")


@_blank_or_rebuild("SF005", consent.generate_sf005)
def generate_sf005(form, config, output_dir):
    """SF005 免取得知情同意檢核表 (主持人填寫欄; 審查委員欄保留空白)."""
    form.put("KFSYSCC-IRB編號", _irb_no(config))
    form.put("計畫名稱", config["study"]["title_zh"])
    yes = set(config["subjects"].get("waiver_criteria") or [3, 4])
    for n, anchor in SF005_CRITERIA.items():
        tr = form.row(anchor)
        if tr is None:
            continue
        tcs = tr.findall(qn("w:tc"))
        if len(tcs) >= 3:
            form.set_cell(tcs[1 if n in yes else 2], "■")
    p = form.find_paragraph("主持人說明")
    if p is not None:
        reason = form.insert_after(p, _waiver_reason(config))
        for r in reason.iter(qn("w:r")):
            Run(r, None).bold = False
    else:
        form.missing.append("主持人說明")
    return _finish(form, "SF005", config, output_dir, "免取得知情同意檢核表")


# ---------------------------------------------------------------------------
# SF022 — 資料及安全性監測計畫 (header + checkable facts; narrative by hand)
# ---------------------------------------------------------------------------

@_blank_or_rebuild("SF022", new_case.generate_sf022)
def generate_sf022(form, config, output_dir):
    """SF022 資料及安全性監測計畫: header, enrolment, vulnerable population."""
    _header_cells(form, config)
    form.sub(r"預計收案人數[:：][ \t　]*人",
             f"預計收案人數：{config['subjects']['planned_n']} 人")
    if not config["study"].get("drug_device"):
        form.check("不適用", scope=form.row("試驗藥品/醫療器材名稱"))
    form.check("是" if config["subjects"].get("vulnerable_population") else "否",
               scope=form.row("研究參與者是否為易受傷害族群"))
    return _finish(form, "SF022", config, output_dir, "資料及安全性監測計畫")


# ---------------------------------------------------------------------------
# SF094 — 顯著財務利益暨非財務關係申報表: one per team member
# ---------------------------------------------------------------------------

ROLE_OPTION = {"pi": "計畫主持人", "co_pi": "協同計畫主持人", "staff": "其他研究團隊成員"}


def _fill_sf094(form, config, role, person):
    _header_cells(form, config, irb_label="SYSCC-IRB編號")
    form.cell("試驗委託者名", config["study"].get("sponsor") or "無")
    form.cell("經費來源", _funding(config))
    r = form.row("研究人員姓名", head=True)
    if r is not None:
        # the name has no cell of its own: give it a line above the role options
        tcs = r.findall(qn("w:tc"))
        first = tcs[-1].find(qn("w:p"))
        form.insert_before(first, f"姓名：{person.get('name', '')}")
        form.check(ROLE_OPTION[role], scope=r)
    if not person.get("conflict_of_interest"):
        form.check("無任何需揭露之顯著財務利益")


def generate_sf094(config, output_dir):
    """SF094 顯著財務利益申報表 — one form per PI / co-PI / staff member."""
    blank = blank_path_or_none("SF094")
    if blank is None:
        print("    ⚠ SF094: no official blank cached — rebuilt layout "
              "(run `irbh templates` to fill the official form instead)")
        return new_case.generate_sf094(config, output_dir)
    paths = []
    for i, (role, person) in enumerate(_team(config)):
        form = Form(blank)
        _fill_sf094(form, config, role, person)
        paths.append(_finish(form, "SF094", config, output_dir, "顯著財務利益申報表",
                             name=None if i == 0 else person.get("name", str(i))))
    return paths


# ---------------------------------------------------------------------------
# 中文計畫摘要 — the official 11 headings, content from proposal.summary_sections
# ---------------------------------------------------------------------------

def _set_size(p, size_pt):
    for r in p.iter(qn("w:r")):
        Run(r, None).font.size = Pt(size_pt)


def _page_footer(form, text):
    """'版本：…　日期：…　第 X 頁，共 Y 頁' with live PAGE / NUMPAGES fields."""
    footer = form.doc.sections[0].footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = 1  # center
    font = form_font()
    rpr = (f'<w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" '
           f'w:cs="{font}"/><w:sz w:val="20"/></w:rPr>')

    def run(t):
        p._p.append(parse_xml(f'<w:r {nsdecls("w")}>{rpr}<w:t xml:space="preserve">{t}</w:t></w:r>'))

    def field(instr):
        p._p.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr=" {instr} ">'
                              f'<w:r>{rpr}<w:t>1</w:t></w:r></w:fldSimple>'))
    run(text + "　第 ")
    field("PAGE")
    run(" 頁，共 ")
    field("NUMPAGES")
    run(" 頁")


@_blank_or_rebuild("PROPOSAL", proposal.generate_proposal_summary)
def generate_proposal_summary(form, config, output_dir):
    """中文計畫摘要 on the official blank: 11 headings, 12 pt body, versioned footer."""
    body = form.body
    # the 填寫說明 box is guidance for the applicant, not part of the submission
    tbl = form.table("填寫說明")
    if tbl is not None:
        body.remove(tbl)

    paras = [c for c in body if c.tag == qn("w:p")]
    sections = proposal.summary_sections(config)
    heads, k = [], 0
    for title, _ in sections:
        rx = re.compile(r"^\s*" + re.escape(title))
        while k < len(paras) and not rx.match(_ptext(paras[k])):
            k += 1
        if k == len(paras):
            form.missing.append(title)
            heads.append(None)
            k = 0
            continue
        heads.append(paras[k])
        k += 1

    end_marker = form.find_paragraph("（以下空白）")
    like = None
    for i, ((_, text), head) in enumerate(zip(sections, heads, strict=True)):
        if head is None:
            continue
        # placeholders between this heading and the next (empty lines, 　)
        nxt = next((h for h in heads[i + 1:] if h is not None), end_marker)
        sib = head.getnext()
        while sib is not None and sib is not nxt and sib.tag == qn("w:p") and not _ptext(sib).strip():
            like = like if like is not None else sib
            after = sib.getnext()
            if sib.find(f"{qn('w:pPr')}/{qn('w:sectPr')}") is None:
                body.remove(sib)
            sib = after
        # trailing line breaks / full-width spaces inside the heading itself
        t = _ptext(head)
        m = re.search(r"\s+$", t)
        if m:
            form.sub(re.escape(t[m.start():]) + "$", "", scope=head)
        prev = head
        for line in text.split("\n"):
            prev = form.insert_after(prev, line, like=like if like is not None else head)
            _set_size(prev, 12)

    study = config["study"]
    version = study.get("doc_version") or "1.0"
    date = study.get("doc_date") or datetime.date.today().strftime("%Y/%m/%d")
    _page_footer(form, f"版本：{version}　日期：{date}")
    return _finish(form, "中文計畫摘要", config, output_dir, "待核發")
