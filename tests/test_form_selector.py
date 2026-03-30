"""Tests for form_selector.py."""
import pytest
import yaml
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.form_selector import select_forms, get_generator, FORM_REGISTRY


@pytest.fixture
def retro_config():
    with open("tests/fixtures/sample_retrospective.yml") as f:
        return yaml.safe_load(f)


def test_retrospective_new_case_selects_correct_forms(retro_config):
    retro_config["phase"] = "new"
    forms = select_forms(retro_config)
    form_ids = [fid for fid, _ in forms]
    # Must include base forms + expedited + consent waiver
    assert "SF001" in form_ids
    assert "SF002" in form_ids
    assert "SF094" in form_ids
    assert "SF003" in form_ids  # expedited review
    assert "SF005" in form_ids  # consent waiver
    # Must NOT include consent forms (waiver applies)
    assert "SF062" not in form_ids
    assert "SF063" not in form_ids
    # Must NOT include drug trial forms
    assert "SF090" not in form_ids


def test_retrospective_closure_selects_correct_forms(retro_config):
    retro_config["phase"] = "closure"
    forms = select_forms(retro_config)
    form_ids = [fid for fid, _ in forms]
    assert "SF036" in form_ids
    assert "SF037" in form_ids
    assert "SF038" in form_ids
    assert "SF023" in form_ids
    assert len(form_ids) == 4


def test_drug_trial_adds_consent_forms():
    config = {
        "study": {"type": "clinical_trial", "review_type": "full_board",
                  "drug_device": True, "genetic": False, "multicenter": False},
        "subjects": {"consent_waiver": False, "vulnerable_population": False},
        "phase": "new",
    }
    forms = select_forms(config)
    form_ids = [fid for fid, _ in forms]
    assert "SF063" in form_ids  # clinical trial consent
    assert "SF090" in form_ids  # drug trial consent
    assert "SF005" not in form_ids  # no consent waiver


def test_amendment_forms():
    config = {
        "study": {"drug_device": False},
        "phase": "amendment",
    }
    forms = select_forms(config)
    form_ids = [fid for fid, _ in forms]
    assert "SF014" in form_ids
    assert "SF015" in form_ids
    assert "SF016" in form_ids
    assert "SF094" in form_ids


def test_unknown_phase_raises():
    config = {"study": {"type": "retrospective"}, "subjects": {"consent_waiver": True}, "phase": "unknown"}
    with pytest.raises(ValueError, match="Unknown phase"):
        select_forms(config)


def test_all_phases_return_forms(retro_config):
    for phase in ["new", "amendment", "continuing", "closure", "suspension", "appeal"]:
        retro_config["phase"] = phase
        forms = select_forms(retro_config)
        assert len(forms) > 0, f"Phase {phase} returned no forms"


def test_get_generator_returns_tuple():
    result = get_generator("SF001")
    assert result is not None
    mod_path, func_name = result
    assert "new_case" in mod_path
    assert func_name == "generate_sf001"


def test_get_generator_unknown_returns_none():
    assert get_generator("SF999") is None


def test_form_registry_completeness():
    """All forms in phase rules should be in registry."""
    from scripts.form_selector import PHASE_FORMS
    for phase, rules in PHASE_FORMS.items():
        for fid in rules["base"]:
            assert fid in FORM_REGISTRY, f"{fid} in {phase} base not in registry"
