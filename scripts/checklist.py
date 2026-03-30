"""Plain-text checklist generator using ■/□ convention."""
import os
from datetime import date


def generate_checklist(config, results, phase_zh, output_path="checklist.md"):
    """Generate checklist.md from generation results.

    Args:
        config: Study config dict
        results: list of (form_id, name_zh, path_or_None, status)
        phase_zh: Chinese phase name
        output_path: Where to write checklist
    """
    irb_no = config["study"]["irb_no"]
    title_zh = config["study"]["title_zh"]
    today = date.today().strftime("%Y-%m-%d")

    lines = [
        f"# IRB Submission Checklist",
        f"## Study: {irb_no} — {title_zh}",
        f"## Phase: {phase_zh}",
        f"## Generated: {today}",
        "",
        "---",
        "",
        "### Generated Forms",
    ]

    for fid, name_zh, path, status in results:
        if status == "generated" and path:
            basename = os.path.basename(path)
            lines.append(f"■ {fid} {name_zh} → {basename}")
        elif status == "error":
            lines.append(f"□ {fid} {name_zh} → GENERATION ERROR")
        elif status == "missing":
            lines.append(f"□ {fid} {name_zh} → NO GENERATOR (manual fill required)")

    lines.extend([
        "",
        "### PDF Conversion",
        "□ Run `python scripts/convert.py` to generate PDFs and previews",
        "",
        "### Manual Steps",
    ])

    # Phase-specific manual steps
    if config["phase"] == "new":
        lines.extend([
            "□ Review and complete 中文計畫摘要",
            "□ Attach 研究計畫書 (study protocol)",
            "□ Attach 主持人學經歷 (PI CV)",
            "□ PI signature on SF002",
            "□ PI signature on SF094",
        ])
    elif config["phase"] == "closure":
        lines.extend([
            "□ Complete SF038 結案報告書 content sections",
            "□ PI signature on SF037",
        ])
    elif config["phase"] == "amendment":
        lines.extend([
            "□ Complete SF016 修正前後對照表 with tracked changes",
            "□ PI signature on SF015",
        ])
    elif config["phase"] == "continuing":
        lines.extend([
            "□ PI signature on SF031",
        ])

    # Common manual steps
    lines.extend([
        "",
        "### Submission",
        "□ Email electronic copies to irb@kfsyscc.org",
        "□ Submit paper copies (1 original + 1 copy) to IRB office",
        "",
        "---",
    ])

    # Summary
    generated = sum(1 for _, _, _, s in results if s == "generated")
    total = len(results)
    lines.append(f"**Status: {generated}/{total} forms generated**")

    content = "\n".join(lines) + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path
