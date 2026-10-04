"""Tests for the config.toml loader and its @file references."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import ConfigError, load_config, main, parse_markdown

MINIMAL = '''
phase = "new"
pi = "@cv.toml#pi"
[study]
title_zh = "測試"
type = "retrospective"
review_type = "expedited"
[dates]
study_start = "2026年01月01日"
study_end = "2026年12月31日"
[subjects]
planned_n = 10
'''


def write(tmp_path, files):
    for name, text in files.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    return str(tmp_path / "config.toml")


def test_examples_resolve_references():
    cfg = load_config("examples/gcsf-retrospective/config.toml")
    assert cfg["pi"]["name"] == "林協霆"
    assert cfg["co_pi"][0]["name"] == "邱倫維"
    prop = load_config("examples/tdxd-her2low/config.toml")["proposal"]
    assert prop["objectives"][0].startswith("主要目的")
    assert "DESTINY-Breast04 與 DESTINY-Breast06" in prop["background"]


def test_root_config_is_valid():
    assert load_config("config.toml")["pi"]["name"]


def test_markdown_sections_lists_and_paragraphs():
    md = """# 中文計畫摘要
<!-- guidance that must not leak -->
## 二、研究背景
第一行
第二行 with English
words here

第二段。
## 納入條件
- 年滿20歲
  且確診
1. **第二點**
## Custom Key
text
"""
    out = parse_markdown(md)
    assert out["background"] == "第一行第二行 with English words here\n第二段。"
    assert out["inclusion"] == ["年滿20歲且確診", "第二點"]
    assert out["Custom Key"] == "text"
    assert "guidance" not in str(out)


def test_markdown_without_headings_is_text():
    assert parse_markdown("# Title\n\n修正內容\n第二行") == "修正內容第二行"


def test_reference_to_whole_markdown_and_phase_override(tmp_path):
    path = write(tmp_path, {
        "config.toml": MINIMAL.replace('[study]', 'proposal = "@sub/摘要.md"\n[study]'),
        "cv.toml": '[pi]\nname = "甲"\ndept = "內科"\n',
    })
    os.mkdir(tmp_path / "sub")
    (tmp_path / "sub" / "摘要.md").write_text("## 統計分析\nCox", encoding="utf-8")
    cfg = load_config(path, phase="closure")
    assert cfg["proposal"] == {"statistics": "Cox"}
    assert cfg["phase"] == "closure"


@pytest.mark.parametrize("files, message", [
    ({"config.toml": MINIMAL}, "file not found"),
    ({"config.toml": MINIMAL, "cv.toml": "[x]\n"}, "no key/section 'pi'"),
    ({"config.toml": MINIMAL.replace('title_zh = "測試"', ''),
      "cv.toml": '[pi]\nname = "甲"\ndept = "內科"\n'}, "study.title_zh"),
    ({"config.toml": MINIMAL.replace('"new"', '"later"'),
      "cv.toml": '[pi]\nname = "甲"\ndept = "內科"\n'}, "unknown phase"),
    ({"config.toml": MINIMAL.replace('"@cv.toml#pi"', '"@loop.toml"'),
      "loop.toml": 'x = "@config.toml"\n'}, "circular reference"),
])
def test_errors_are_explicit(tmp_path, files, message):
    with pytest.raises(ConfigError, match=message):
        load_config(write(tmp_path, files))


def test_cli_shell_output_is_quoted(capsys):
    assert main(["examples/tdxd-her2low/config.toml", "--shell", "--phase", "closure"]) == 0
    out = capsys.readouterr().out
    assert "PHASE=closure" in out and "PI='林協霆'" in out
