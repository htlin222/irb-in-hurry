"""config.toml loading: @file references, validation, defaults and phase switching."""
import os
import tomllib

import pytest

from irb_in_hurry.config import ConfigError, load_config, main, parse_markdown, validate_config
from irb_in_hurry.set_phase import set_phase

RETRO = "irb_in_hurry/examples/gcsf-retrospective/config.toml"

MINIMAL = '''
phase = "new"
pi = "@cv.toml#pi"
[study]
title_zh = "測試"
title_en = "Test"
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
    cfg = load_config("irb_in_hurry/examples/gcsf-retrospective/config.toml")
    assert cfg["pi"]["name"] == "林協霆"
    assert cfg["co_pi"][0]["name"] == "邱倫維"
    prop = load_config("irb_in_hurry/examples/tdxd-her2low/config.toml")["proposal"]
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
    assert main(["irb_in_hurry/examples/tdxd-her2low/config.toml", "--shell", "--phase", "closure"]) == 0
    out = capsys.readouterr().out
    assert "PHASE=closure" in out and "PI='林協霆'" in out


# ── Validation (on the resolved dict) ───────────────────────────────────────

@pytest.fixture
def raw_config():
    """The retrospective example, resolved but not yet validated."""
    cfg = load_config(RETRO)
    with open(RETRO, "rb") as f:
        raw = tomllib.load(f)
    # keep the resolved team, drop everything validation added
    raw["pi"], raw["co_pi"] = dict(cfg["pi"]), [dict(c) for c in cfg["co_pi"]]
    return raw


def test_fixture_validates(raw_config):
    config = validate_config(raw_config)
    assert config["pi"]["name"] == "林協霆"
    assert config["co_pi"][0]["name"] == "邱倫維"


def test_optional_sections_get_defaults(raw_config):
    for key in ("co_pi", "closure", "amendment", "continuing_review"):
        raw_config.pop(key, None)
    raw_config["pi"].pop("phone", None)
    config = validate_config(raw_config)
    assert config["co_pi"] == []
    assert config["closure"]["data_safety"] == {}
    assert config["amendment"] == {}
    assert config["pi"]["phone"] == ""


def test_all_problems_reported_at_once(raw_config):
    raw_config["study"]["title_zh"] = ""
    del raw_config["pi"]["name"]
    raw_config["phase"] = "closing"
    with pytest.raises(ConfigError) as exc:
        validate_config(raw_config)
    msg = str(exc.value)
    assert "3 problem" in msg
    assert "study.title_zh" in msg and "pi.name" in msg and "closing" in msg


def test_quoted_boolean_rejected(raw_config):
    """"false" in quotes is a truthy string and would select the wrong forms."""
    raw_config["study"]["drug_device"] = "false"
    with pytest.raises(ConfigError, match="study.drug_device"):
        validate_config(raw_config)


def test_quoted_boolean_rejected_from_file(tmp_path):
    path = write(tmp_path, {
        "config.toml": MINIMAL.replace('review_type = "expedited"', 'review_type = "expedited"\ngenetic = "false"'),
        "cv.toml": '[pi]\nname = "甲"\ndept = "內科"\n',
    })
    with pytest.raises(ConfigError, match="study.genetic"):
        load_config(path)


@pytest.mark.parametrize("field,value", [("type", "retro"), ("review_type", "expidited")])
def test_enum_typos_rejected(raw_config, field, value):
    raw_config["study"][field] = value
    with pytest.raises(ConfigError, match=value):
        validate_config(raw_config)


def test_unknown_institution_rejected(raw_config, monkeypatch):
    monkeypatch.delenv("IRB_INSTITUTION", raising=False)
    raw_config["institution"] = "no_such_irb"
    with pytest.raises(ConfigError, match="no_such_irb"):
        validate_config(raw_config)


def test_wrong_section_type_rejected(tmp_path):
    path = write(tmp_path, {
        "config.toml": MINIMAL.replace('"@cv.toml#pi"', '"@pi.md"'),
        "pi.md": "王大明",
    })
    with pytest.raises(ConfigError, match="`pi` must be a table"):
        load_config(path)


@pytest.mark.parametrize("text", ["", "phase = \"new\"\nstudy = 1\n", "phase = \"new\"\n[study\n"])
def test_malformed_toml_rejected(tmp_path, text):
    path = tmp_path / "config.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(str(path))


# ── set_phase ───────────────────────────────────────────────────────────────

def test_set_phase_keeps_comments(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('# keep me\nphase = "new"   # new | closure\n\n[study]\nirb_no = "X"  # and me\n'
                    'phase = "not top-level"\n', encoding="utf-8")
    set_phase(str(path), "closure")
    text = path.read_text(encoding="utf-8")
    assert "# keep me" in text and "# and me" in text and "# new | closure" in text
    assert 'phase = "closure"' in text and 'phase = "new"' not in text
    assert 'phase = "not top-level"' in text
    with open(path, "rb") as f:
        assert tomllib.load(f)["phase"] == "closure"
    with pytest.raises(ValueError):
        set_phase(str(path), "closing")


def test_set_phase_adds_missing_key_at_top_level(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('pi = "@cv.toml#pi"\n\n[study]\ntitle_zh = "x"\n', encoding="utf-8")
    set_phase(str(path), "amendment")
    with open(path, "rb") as f:
        data = tomllib.load(f)
    assert data["phase"] == "amendment" and "phase" not in data["study"]
