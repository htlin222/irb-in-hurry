#!/usr/bin/env python3
"""Load the study's single source of truth: config.toml + the files it references.

config.toml holds structured study metadata. Any string value of the form
``"@path"`` or ``"@path#key"`` is replaced by the referenced file's content,
resolved relative to the file that contains it:

    pi       = "@cv.toml#pi"          # a table from another TOML file
    co_pi    = "@cv.toml#co_pi"       # an array of tables
    proposal = "@中文計畫摘要.md"      # Markdown: one key per `## heading`
    [amendment]
    change_description = "@修正說明.md"  # Markdown without headings → plain text

Markdown rules: ``## heading`` starts a section (``二、`` style numbering is
ignored and Chinese headings map to keys via SECTION_KEYS); a section made only
of ``-``/``1.`` items becomes a list; other text becomes paragraphs; HTML
comments are dropped, so templates can carry writing guidance.

After resolution the config is validated and every problem is reported at once
(required fields, unknown phase / study.type / study.review_type, quoted
booleans), and optional sections are filled with neutral defaults so
generators can index them directly.
Field reference: .claude/skills/irb/references/config-schema.md

CLI:
    python scripts/config.py [config.toml] [--phase X]           # check + summary
    python scripts/config.py [config.toml] [--phase X] --json    # resolved config
    python scripts/config.py [config.toml] [--phase X] --shell   # for dashboard.sh
"""
import argparse
import importlib
import json
import os
import re
import shlex
import sys
import tomllib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import institution  # noqa: E402
from scripts.form_selector import PHASE_NAMES  # noqa: E402

# Markdown `## heading` → config key. Unlisted headings are used verbatim.
SECTION_KEYS = {
    "研究背景": "background",
    "研究目的": "objectives",
    "研究設計": "design",
    "納入條件": "inclusion",
    "排除條件": "exclusion",
    "資料收集項目": "variables",
    "研究終點": "endpoints",
    "研究方法": "methods",
    "統計分析": "statistics",
    "附件": "attachments",
}

STUDY_TYPES = ("retrospective", "prospective", "clinical_trial", "genetic")
REVIEW_TYPES = ("exempt", "expedited", "full_board")

# (section, field) pairs that must be present and non-empty
REQUIRED = [
    ("study", "title_zh"), ("study", "title_en"), ("study", "type"), ("study", "review_type"),
    ("pi", "name"), ("pi", "dept"),
    ("dates", "study_start"), ("dates", "study_end"),
    ("subjects", "planned_n"),
]

# Optional fields that generators index directly → default.
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

# Fields that must be real TOML booleans: a quoted "false" is a non-empty string
# and would silently count as true when selecting forms.
BOOL_FIELDS = [
    ("study", "drug_device"), ("study", "genetic"), ("study", "multicenter"),
    ("subjects", "consent_waiver"), ("subjects", "vulnerable_population"),
    ("amendment", "affects_consent"), ("amendment", "affects_risk"),
    ("continuing_review", "extension_requested"), ("closure", "specimens"),
]

_CJK = r"　-〿一-鿿＀-￯"


class ConfigError(ValueError):
    """Config cannot be loaded, is missing required data or has invalid values."""


# ── Markdown ────────────────────────────────────────────────────────────────

def _join(lines):
    """Join wrapped lines: no space next to CJK, one space between Latin words."""
    out = ""
    for line in lines:
        line = line.strip()
        if out and line and not (re.match(f"[{_CJK}]", out[-1]) or re.match(f"[{_CJK}]", line[0])):
            out += " "
        out += line
    return out


def _inline(text):
    """Drop inline Markdown emphasis/code markers; DOCX output is plain text."""
    return re.sub(r"(\*\*|__|`)", "", text)


_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")


def _block(body):
    """Section body → list (all items) or paragraph string."""
    lines = body.strip("\n").splitlines()
    if not any(ln.strip() for ln in lines):
        return ""
    starts = [ln for ln in lines if ln.strip() and not ln.startswith((" ", "\t"))]
    if starts and all(_ITEM.match(ln) for ln in starts):
        items = []
        for ln in lines:
            m = _ITEM.match(ln) if not ln.startswith((" ", "\t")) else None
            if m:
                items.append([m.group(1)])
            elif ln.strip():
                items[-1].append(ln)  # continuation line
        return [_inline(_join(i)) for i in items]
    paras = re.split(r"\n\s*\n", "\n".join(lines))
    return "\n".join(_inline(_join(p.splitlines())) for p in paras if p.strip())


def _section_key(heading):
    h = re.sub(r"^(?:[一二三四五六七八九十]+、|\d+[.、)]\s*)", "", heading.strip())
    return SECTION_KEYS.get(h, h)


def parse_markdown(text):
    """Markdown → dict of `## sections`, or plain text when there are none."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    parts = re.split(r"^##[ \t]+(.+?)[ \t#]*$", text, flags=re.M)
    if len(parts) == 1:
        body = "\n".join(ln for ln in text.splitlines() if not ln.startswith("# "))
        return _block(body)
    return {_section_key(h): _block(b) for h, b in zip(parts[1::2], parts[2::2], strict=True)}


# ── References ──────────────────────────────────────────────────────────────

def _read(path):
    if path.endswith(".toml"):
        with open(path, "rb") as f:
            return tomllib.load(f)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return parse_markdown(text) if path.endswith(".md") else text.strip()


def _resolve(value, base, stack):
    if isinstance(value, dict):
        return {k: _resolve(v, base, stack) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v, base, stack) for v in value]
    if not (isinstance(value, str) and value.startswith("@")):
        return value

    ref, _, key = value[1:].partition("#")
    path = os.path.normpath(os.path.join(base, ref))
    if path in stack:
        raise ConfigError(f"circular reference: {' → '.join(stack + [path])}")
    if not os.path.isfile(path):
        raise ConfigError(f"{value!r}: file not found ({path})")
    data = _read(path)
    if key:
        if not isinstance(data, dict) or key not in data:
            raise ConfigError(f"{value!r}: no key/section {key!r} in {ref}")
        data = data[key]
    return _resolve(data, os.path.dirname(path), stack + [path])


# ── Validation ──────────────────────────────────────────────────────────────

def _apply_defaults(config):
    for section, default in DEFAULTS.items():
        if config.get(section) is None:
            config[section] = {} if isinstance(default, dict) else list(default)
        if isinstance(default, dict):
            for key, value in default.items():
                if config[section].get(key) is None:
                    config[section][key] = value.copy() if isinstance(value, (dict, list)) else value


def validate_config(config, source="config.toml"):
    """Validate and normalize a resolved config dict in place. Raises ConfigError listing every problem."""
    if not isinstance(config, dict):
        raise ConfigError(f"{source}: expected a table, got {type(config).__name__}")

    problems = []
    for section, default in DEFAULTS.items():
        if config.get(section) is not None and not isinstance(config[section], type(default)):
            kind = "a table" if isinstance(default, dict) else "an array of tables"
            problems.append(f"`{section}` must be {kind}")
    if problems:
        raise ConfigError(f"{source}:\n  - " + "\n  - ".join(problems))

    _apply_defaults(config)

    for section, field in REQUIRED:
        if str(config[section].get(field, "")).strip() == "":
            problems.append(f"`{section}.{field}` is required")

    # Phases are checked against the form pack of the institution this config
    # selects (IRB_INSTITUTION env > `institution` > default).
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
        problems.append(f"unknown phase: `phase` must be one of {', '.join(phases)} (got {phase!r})")

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


def load_config(path="config.toml", phase=None):
    """Load config.toml, inline every @reference, apply a phase override, validate."""
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise ConfigError(f"config not found: {path}")
    try:
        config = _resolve(_read(path), os.path.dirname(path), [path])
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"invalid TOML: {e}") from e
    if phase:
        config["phase"] = phase
    return validate_config(config, source=os.path.basename(path))


# ── CLI ─────────────────────────────────────────────────────────────────────

def _summary(config, path):
    s, prop = config["study"], config.get("proposal") or {}
    team = [config["pi"]["name"]] + [c["name"] for c in config.get("co_pi", [])]
    print(f"■ {path} OK")
    print(f"  Phase:    {PHASE_NAMES[config['phase']]} ({config['phase']})")
    print(f"  IRB No:   {s.get('irb_no') or '（待核發）'}")
    print(f"  Title:    {s['title_zh']}")
    print(f"  Type:     {s['type']} / {s.get('design', '')} / {s['review_type']}")
    print(f"  Team:     {'、'.join(team)}")
    if isinstance(prop, dict) and prop:
        print(f"  摘要章節: {', '.join(prop)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("config", nargs="?", default="config.toml")
    ap.add_argument("--phase", default=os.environ.get("PHASE") or None)
    fmt = ap.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", help="print the resolved config")
    fmt.add_argument("--shell", action="store_true", help="print shell variables")
    args = ap.parse_args(argv)

    try:
        config = load_config(args.config, args.phase)
    except ConfigError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(config, ensure_ascii=False, indent=2))
    elif args.shell:
        s = config["study"]
        for name, val in [
            ("INSTITUTION", institution.resolve_id(config).upper()),
            ("IRB_NO", s.get("irb_no", "")), ("PHASE", config["phase"]),
            ("PHASE_ZH", PHASE_NAMES[config["phase"]]), ("TITLE", s["title_zh"][:40]),
            ("PI", config["pi"]["name"]), ("STUDY_TYPE", s["type"]),
            ("REVIEW_TYPE", s["review_type"]),
        ]:
            print(f"{name}={shlex.quote(str(val))}")
    else:
        _summary(config, args.config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
