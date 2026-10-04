"""Draft cover letter (致人體試驗委員會函稿) for each submission phase.

Writes a polite, formal Chinese letter that can be pasted into the email to
irb@kfsyscc.org or printed as 送審函. Study facts come from config.yml; anything
the config does not hold is left as a 【請填寫：…】 placeholder so the PI can
see exactly what still needs their words.
"""
import os
import re
from datetime import date

PH = "【請填寫：{}】"

STUDY_TYPE_ZH = {
    "retrospective": "回溯性研究",
    "prospective": "前瞻性觀察研究",
    "clinical_trial": "臨床試驗",
    "genetic": "基因研究",
}
REVIEW_TYPE_ZH = {
    "exempt": "免予審查",
    "expedited": "簡易審查",
    "full_board": "一般審查",
}


def _ph(what):
    return PH.format(what)


def _or_ph(value, what):
    """Config value if present, else a fill-in placeholder."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return _ph(what)
    return str(value)


def _today_zh():
    d = date.today()
    return f"{d.year}年{d.month:02d}月{d.day:02d}日"


def _count(n, unit, what, none):
    """'計畫展延 2 次' or, when zero, the softer '未曾展延'."""
    return none if not n else f"{what} {n} {unit}"


def _yn(flag, yes, no):
    return yes if flag else no


# ── Phase bodies ────────────────────────────────────────────────────────────
# Each returns (subject_suffix, [paragraphs]). Paragraphs are joined with a
# blank line and indented by two full-width spaces, as in a formal 公文-style letter.

def _body_new(c, ctx):
    s, subj = c["study"], c["subjects"]
    review = REVIEW_TYPE_ZH.get(s.get("review_type"), _ph("審查類別"))
    stype = STUDY_TYPE_ZH.get(s.get("type"), _ph("研究類型"))
    paras = [
        f"本人擬於本院執行「{s['title_zh']}」，謹檢送新案申請相關文件，"
        f"敬請 鈞會惠予{review}。",
        f"本研究為{stype}，預計納入 {_or_ph(subj.get('planned_n'), '預計人數')} 位研究參與者，"
        f"研究期間自 {_or_ph(c['dates'].get('study_start'), '起始日')} 至 "
        f"{_or_ph(c['dates'].get('study_end'), '結束日')}。"
        + (f"資料收集範圍為 {c['dates']['data_period']} 之病歷紀錄。"
           if c["dates"].get("data_period") else ""),
    ]
    if subj.get("consent_waiver"):
        paras.append(
            "因本研究僅使用既有病歷資料，對研究參與者之風險不高於最小風險，"
            "且資料將於分析前去識別化，故一併申請免除取得研究參與者同意，"
            "相關理由詳見免取得知情同意檢核表。"
        )
    paras.append(
        "本人與研究團隊將恪遵 鈞會核准之計畫內容執行研究，"
        "並善盡保護研究參與者權益與個人資料之責。"
    )
    return "新案審查", paras


def _body_amendment(c, ctx):
    a = c.get("amendment", {}) or {}
    paras = [
        f"本人擔任計畫主持人之「{c['study']['title_zh']}」（IRB 編號：{ctx['irb_no']}），"
        f"業蒙 鈞會於 {ctx['approval']} 核准執行，衷心感謝。",
        f"因{_or_ph(a.get('change_description'), '修正原因與內容摘要')}，"
        "擬提出計畫修正，修正前後內容詳見修正前後對照表。",
        "經評估，本次修正"
        + _yn(a.get("affects_risk"), "可能影響研究參與者之風險，相關因應措施已併同說明", "不增加研究參與者之風險")
        + "，且"
        + _yn(a.get("affects_consent"), "涉及受試者同意書之修訂，已一併檢附修訂版本", "不涉及受試者同意書之修訂")
        + "。",
        "敬請 鈞會惠予審查。",
    ]
    return "修正案審查", paras


def _body_re_review(c, ctx):
    paras = [
        f"承蒙 鈞會審閱本人擔任計畫主持人之「{c['study']['title_zh']}」"
        f"（IRB 編號：{ctx['irb_no']}），並惠賜寶貴意見，謹致謝忱。",
        f"本人已依 鈞會 {_ph('審查意見函日期')} 之審查意見逐點檢視，"
        "並修正相關文件；各項意見之回覆說明及修正處，詳見複審案申請表。",
        f"主要修正如下：{_ph('逐點簡述修正重點，例如：一、…；二、…')}",
        "如尚有未盡周全之處，懇請 鈞會不吝指正，本人當即配合補正。",
    ]
    return "複審案審查（審查意見回覆）", paras


def _body_continuing(c, ctx):
    cr = c.get("continuing_review", {}) or {}
    subj = c["subjects"]
    paras = [
        f"本人擔任計畫主持人之「{c['study']['title_zh']}」（IRB 編號：{ctx['irb_no']}），"
        f"業蒙 鈞會於 {ctx['approval']} 核准執行，謹依規定檢送期中報告，敬請 鈞會惠予審查。",
        f"截至目前，本計畫{_or_ph(cr.get('enrollment_status'), '執行／收案現況')}，"
        f"已納入 {_or_ph(subj.get('actual_n'), '已收案人數')} 位研究參與者"
        f"（預計 {_or_ph(subj.get('planned_n'), '預計人數')} 位）。"
        "執行期間"
        + _count(cr.get("deviations"), "件", "共發生計畫偏離", "未發生計畫偏離")
        + "，研究參與者之安全與權益均獲妥善維護。",
    ]
    if cr.get("extension_requested"):
        paras.append(
            f"因{_ph('展延原因')}，本計畫擬申請展延執行期限至 {_ph('展延後結束日')}，"
            "已併附計畫展延申請表。"
        )
    paras.append("本人將持續依核准計畫內容執行，並適時向 鈞會報告。")
    return "期中審查", paras


def _body_closure(c, ctx):
    cl = c.get("closure", {}) or {}
    ds = cl.get("data_safety", {}) or {}
    subj = c["subjects"]
    paras = [
        f"本人擔任計畫主持人之「{c['study']['title_zh']}」（IRB 編號：{ctx['irb_no']}），"
        f"業蒙 鈞會於 {ctx['approval']} 核准執行，現已於 "
        f"{_or_ph(c['dates'].get('study_end'), '計畫結束日')} 執行完畢，"
        "謹檢送結案報告相關文件，敬請 鈞會惠予審查。",
        f"本計畫實際納入 {_or_ph(subj.get('actual_n'), '實際收案人數')} 位研究參與者"
        f"（預計 {_or_ph(subj.get('planned_n'), '預計人數')} 位）；"
        "執行期間"
        + "、".join([
            _count(cl.get("extensions"), "次", "計畫展延", "未曾展延"),
            _count(cl.get("amendments"), "次", "計畫修正", "未曾修正"),
            _count(cl.get("sae_count"), "件", "發生嚴重不良事件", "未發生嚴重不良事件"),
        ])
        + "。",
    ]
    safety = []
    if ds.get("deidentified"):
        safety.append("均已去識別化")
    if ds.get("encrypted"):
        safety.append("以加密方式儲存")
    if ds.get("retention_years"):
        safety.append(f"將保存 {ds['retention_years']} 年")
    if ds.get("authorized_personnel"):
        safety.append(f"僅限{ds['authorized_personnel']}存取")
    if safety:
        paras.append("研究資料" + "，".join(safety) + "，期滿後依規定銷毀。")
    paras.append("本計畫承蒙 鈞會悉心指導與監督，得以順利完成，謹此致謝。")
    return "結案審查", paras


def _body_sae(c, ctx):
    paras = [
        f"謹依規定通報本人擔任計畫主持人之「{c['study']['title_zh']}」"
        f"（IRB 編號：{ctx['irb_no']}）所發生之嚴重不良事件。",
        f"事件摘要：{_ph('研究參與者代碼、發生日期、事件經過、與研究之相關性評估')}。",
        f"已採取之處置：{_ph('醫療處置、研究參與者目前狀況、是否需修正計畫或同意書')}。",
        "詳細內容請參閱檢附之通報表。本人將持續追蹤後續情形，並適時向 鈞會補充報告。",
    ]
    return "嚴重不良事件通報", paras


def _body_ib_update(c, ctx):
    paras = [
        f"本人擔任計畫主持人之「{c['study']['title_zh']}」（IRB 編號：{ctx['irb_no']}），"
        f"試驗委託者已更新主持人手冊至 {_ph('版本及日期')}，謹檢送相關文件，敬請 鈞會惠予備查。",
        f"本次更新重點：{_ph('新增之安全性資訊或其他重要變更')}；"
        f"經評估{_ph('是否影響研究參與者風險及受試者同意書')}。",
    ]
    return "主持人手冊更新", paras


def _body_import(c, ctx):
    paras = [
        f"本人擔任計畫主持人之「{c['study']['title_zh']}」（IRB 編號：{ctx['irb_no']}），"
        f"因{_ph('病人需求及國內無替代藥品／醫材之理由')}，"
        f"擬申請專案進口 {_ph('藥品／醫材名稱')}，謹檢送相關文件，敬請 鈞會惠予審查。",
        "本人將確實向病人說明可能之風險與效益，並取得其書面同意後方予使用。",
    ]
    return "專案進口審查", paras


def _body_suspension(c, ctx):
    paras = [
        f"本人擔任計畫主持人之「{c['study']['title_zh']}」（IRB 編號：{ctx['irb_no']}），"
        f"因{_ph('暫停／提前終止之原因')}，擬{_ph('暫停／提前終止')}本計畫，"
        "謹檢送相關報告，敬請 鈞會惠予審查。",
        f"截至目前已納入 {_or_ph(c['subjects'].get('actual_n'), '已收案人數')} 位研究參與者；"
        f"對已參與者之後續照護與通知安排為：{_ph('後續照護、通知方式及資料處理')}。",
        "本人將確保研究參與者之安全與權益不因本計畫暫停或終止而受影響。",
    ]
    return "計畫暫停／提前終止", paras


def _body_appeal(c, ctx):
    paras = [
        f"本人擔任計畫主持人之「{c['study']['title_zh']}」（IRB 編號：{ctx['irb_no']}），"
        f"承蒙 鈞會於 {_ph('審查決議日期')} 審查並惠賜意見，本人深表感謝，亦充分尊重 鈞會之專業判斷。",
        f"惟就{_ph('申覆之審查意見項目')}，本人謹補充說明如下，懇請 鈞會惠予重新考量：",
        _ph("逐點說明申覆理由與佐證資料，語氣宜就事論事、避免爭辯"),
        "如 鈞會認為仍有需補正之處，本人當虛心受教，並即配合修正。",
    ]
    return "申覆案審查", paras


PHASE_BODIES = {
    "new": _body_new,
    "amendment": _body_amendment,
    "re_review": _body_re_review,
    "continuing": _body_continuing,
    "closure": _body_closure,
    "sae": _body_sae,
    "ib_update": _body_ib_update,
    "import": _body_import,
    "suspension": _body_suspension,
    "appeal": _body_appeal,
}


def generate_cover_letter(config, results, output_dir="output"):
    """Write output/IRB_致委員會函稿_<階段>.md and return its path.

    Args:
        config: Study config dict
        results: list of (form_id, name_zh, path_or_None, status) from generate_all
        output_dir: Where to write the letter
    """
    phase = config["phase"]
    if phase not in PHASE_BODIES:
        raise ValueError(f"No cover letter template for phase: {phase}")

    s, pi = config["study"], config["pi"]
    ctx = {
        "irb_no": _or_ph(s.get("irb_no"), "IRB 編號"),
        "approval": _or_ph(config.get("dates", {}).get("irb_approval_date"), "核准日期"),
    }
    label, paras = PHASE_BODIES[phase](config, ctx)

    irb_tag = f"【{s['irb_no']}】" if s.get("irb_no") else ""
    subject = f"{irb_tag}{label}送審－{s['title_zh']}（計畫主持人：{pi['name']}）"

    attachments = [
        f"{fid} {name}" if fid.startswith("SF") else name
        for fid, name, _, status in results if status == "generated"
    ]
    attachments += {
        "new": ["研究計畫書", "計畫主持人學經歷"],
    }.get(phase, [])

    body = [
        "人體試驗委員會 主任委員暨各位委員 鈞鑒：",
        "",
    ]
    for p in paras:
        body += [f"　　{p}", ""]
    body.append("　　檢附文件如下：")
    body += [f"　　{i}. {a}" for i, a in enumerate(attachments, 1)]
    body += [
        "",
        f"　　如有任何疑問或需補充資料之處，敬請不吝賜知，本人當即配合辦理。"
        f"聯絡電話：{_or_ph(pi.get('phone'), '聯絡電話')}；"
        f"電子郵件：{_or_ph(pi.get('email'), '電子郵件')}。",
        "",
        "　　耑此　敬請",
        "鈞安",
        "",
        f"{_or_ph(pi.get('dept'), '單位／職稱')}",
        f"計畫主持人　{pi['name']}　敬上",
        _today_zh(),
    ]
    body_text = "\n".join(body)

    todo = sorted(set(re.findall(r"【請填寫：(.+?)】", subject + body_text)))
    notes = [
        f"# 致人體試驗委員會函稿（{label}）",
        "",
        "> 用途：寄至 irb@kfsyscc.org 的電子郵件內文，或列印為紙本送審函。",
        "> 寄出前請：(1) 補齊下列【請填寫】欄位；(2) 核對檢附文件與實際附件一致；(3) 刪除本說明區塊。",
    ]
    if todo:
        notes.append(">")
        notes.append("> 待補欄位：" + "、".join(todo))

    content = "\n".join(notes + [
        "",
        "---",
        "",
        f"主旨：{subject}",
        "",
        body_text,
        "",
    ])

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"IRB_致委員會函稿_{label.split('（')[0]}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
