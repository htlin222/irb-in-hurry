"""config.yml validation, defaults and phase switching."""
import pytest
import yaml

from scripts.config import ConfigError, load_config, validate_config
from scripts.set_phase import set_phase


@pytest.fixture
def raw_config():
    with open("tests/fixtures/sample_retrospective.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_fixture_loads(raw_config):
    config = validate_config(raw_config)
    assert config["pi"]["name"] == "林協霆"
    assert config["co_pi"][0]["name"] == "邱倫維"


def test_optional_sections_get_defaults(raw_config):
    for key in ("co_pi", "closure", "amendment", "continuing_review"):
        raw_config.pop(key, None)
    del raw_config["pi"]["phone"]
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


@pytest.mark.parametrize("field,value", [("type", "retro"), ("review_type", "expidited")])
def test_enum_typos_rejected(raw_config, field, value):
    raw_config["study"][field] = value
    with pytest.raises(ConfigError, match=value):
        validate_config(raw_config)


@pytest.mark.parametrize("text", ["", "- just\n- a list\n", "study: oops\npi: {}\nphase: new\n"])
def test_malformed_yaml_rejected(tmp_path, text):
    path = tmp_path / "config.yml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(str(path))


def test_set_phase_keeps_comments(tmp_path):
    path = tmp_path / "config.yml"
    path.write_text("# keep me\nstudy:\n  irb_no: \"X\"  # and me\n\nphase: new\n", encoding="utf-8")
    set_phase(str(path), "closure")
    text = path.read_text(encoding="utf-8")
    assert "# keep me" in text and "# and me" in text
    assert "phase: closure" in text and "phase: new" not in text
    with pytest.raises(ValueError):
        set_phase(str(path), "closing")
