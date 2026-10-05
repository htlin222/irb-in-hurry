"""Cover letter drafts: one per phase, facts from config, gaps as placeholders."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import load_config
from scripts.cover_letter import PHASE_BODIES, generate_cover_letter
from scripts.form_selector import PHASE_FORMS, select_forms


def _letter(phase, tmp_path, **overrides):
    config = load_config("examples/gcsf-retrospective/config.toml")
    config["phase"] = phase
    for key, value in overrides.items():
        config["study"][key] = value
    results = [(fid, name, "x.docx", "generated") for fid, name in select_forms(config)]
    path = generate_cover_letter(config, results, str(tmp_path))
    with open(path, encoding="utf-8") as f:
        return path, f.read()


def test_every_phase_has_a_template():
    assert set(PHASE_BODIES) == set(PHASE_FORMS)


@pytest.mark.parametrize("phase", sorted(PHASE_BODIES))
def test_letter_is_formal_and_lists_attachments(phase, tmp_path):
    path, text = _letter(phase, tmp_path)
    assert os.path.basename(path).startswith("IRB_致委員會函稿_")
    assert "主旨：【20250801A】" in text
    assert "鈞鑒" in text and "敬上" in text and "鈞安" in text
    assert "早期乳癌患者接受化療期間" in text
    assert "林協霆" in text and "htlin222@kfsyscc.org" in text
    assert "檢附文件如下" in text


def test_closure_uses_config_facts(tmp_path):
    _, text = _letter("closure", tmp_path)
    assert "882 位" in text
    assert "未發生嚴重不良事件" in text
    assert "保存 7 年" in text
    assert "SF038 結案報告書" in text


def test_new_case_without_irb_no_lists_proposal_and_waiver(tmp_path):
    _, text = _letter("new", tmp_path, irb_no="")
    assert text.count("主旨：新案審查送審") == 1
    assert "免除取得研究參與者同意" in text
    assert "　　4. 中文計畫摘要" in text  # non-SF ids are not shown
    assert "研究計畫書" in text


def test_missing_facts_become_placeholders(tmp_path):
    _, text = _letter("amendment", tmp_path)
    assert "【請填寫：修正原因與內容摘要】" in text
    assert "待補欄位：" in text
