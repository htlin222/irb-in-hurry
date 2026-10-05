"""Load, validate and normalize config.yml.

Every generator reads the same dict, so problems are caught here once, with a
message that names the offending field, instead of surfacing as a KeyError deep
inside a form. Optional fields are filled with neutral defaults so generators
can index them directly. Field reference: .claude/skills/irb/references/config-schema.md
"""
import importlib

import yaml

from scripts import institution
from scripts.form_selector import PHASE_NAMES

STUDY_TYPES = ("retrospective", "prospective", "clinical_trial", "genetic")
REVIEW_TYPES = ("exempt", "expedited", "full_board")

# (section, field) pairs that must be present and non-empty
REQUIRED = [
    ("study", "title_zh"),
    ("study", "title_en"),
    ("pi", "name"),
    ("pi", "dept"),
]

# Optional fields that generators index directly → default. Fields generators
# read with their own .get() fallback (e.g. planned_n → "＿＿") are left alone.
DEFAULTS = {
    "study": {"irb_no": "", "drug_device": False, "genetic": False, "multicenter": False},
    "pi": {"phone": "", "email": ""},
    "co_pi": [],
    "dates": {},
    "subjects": {"consent_waiver": False, "vulnerable_population": False},
    "closure": {"data_safety": {}},
    "amendment": {},
    "continuing_review": {},
}

# Fields that must be real YAML booleans: a quoted "false" is a non-empty string
# and would silently count as true when selecting forms.
BOOL_FIELDS = [
    ("study", "drug_device"), ("study", "genetic"), ("study", "multicenter"),
    ("subjects", "consent_waiver"), ("subjects", "vulnerable_population"),
    ("amendment", "affects_consent"), ("amendment", "affects_risk"),
    ("continuing_review", "extension_requested"), ("closure", "specimens"),
]


class ConfigError(ValueError):
    """config.yml is missing required data or has invalid values."""


def _apply_defaults(config):
    for section, default in DEFAULTS.items():
        if config.get(section) is None:
            config[section] = {} if isinstance(default, dict) else list(default)
        if isinstance(default, dict):
            for key, value in default.items():
                if config[section].get(key) is None:
                    config[section][key] = value.copy() if isinstance(value, (dict, list)) else value


def validate_config(config, source="config.yml"):
    """Validate and normalize a config dict in place. Raises ConfigError listing every problem."""
    if not isinstance(config, dict):
        raise ConfigError(f"{source}: expected a YAML mapping, got {type(config).__name__}")

    problems = []
    for section, default in DEFAULTS.items():
        if config.get(section) is not None and not isinstance(config[section], type(default)):
            kind = "a mapping" if isinstance(default, dict) else "a list"
            problems.append(f"`{section}` must be {kind}")
    if problems:
        raise ConfigError(f"{source}:\n  - " + "\n  - ".join(problems))

    _apply_defaults(config)

    for section, field in REQUIRED:
        if not str(config[section].get(field) or "").strip():
            problems.append(f"`{section}.{field}` is required")

    # Phases are checked against the form pack of the institution this config
    # selects (IRB_INSTITUTION env > `institution:` > default).
    phases = list(PHASE_NAMES)
    inst_id = config.get("institution")
    if inst_id is not None and not (isinstance(inst_id, str) and inst_id.strip()):
        problems.append(f"`institution` must be a folder name under institutions/ (got {inst_id!r})")
    else:
        try:
            profile = institution.load(institution.resolve_id(config))
            phases = list(importlib.import_module(profile.forms_module).PHASE_FORMS)
        except FileNotFoundError as e:
            problems.append(f"`institution`: {e}")

    phase = config.get("phase")
    if phase not in phases:
        problems.append(f"`phase` must be one of {', '.join(phases)} (got {phase!r})")

    study = config["study"]
    for field, allowed in (("type", STUDY_TYPES), ("review_type", REVIEW_TYPES)):
        value = study.get(field)
        if value and value not in allowed:
            problems.append(f"`study.{field}` must be one of {', '.join(allowed)} (got {value!r})")

    for section, field in BOOL_FIELDS:
        value = config[section].get(field, False)
        if not isinstance(value, bool):
            problems.append(f"`{section}.{field}` must be true or false without quotes (got {value!r})")

    for i, cp in enumerate(config["co_pi"]):
        if not isinstance(cp, dict) or not cp.get("name"):
            problems.append(f"`co_pi[{i}]` needs a `name`")
        else:
            cp.setdefault("dept", "")

    if problems:
        raise ConfigError(f"{source} has {len(problems)} problem(s):\n  - " + "\n  - ".join(problems))
    return config


def load_config(path="config.yml"):
    """Load config.yml, validate it and fill optional fields with defaults."""
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return validate_config(config, source=path)
