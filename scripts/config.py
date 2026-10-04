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

CLI:
    python scripts/config.py [config.toml] [--phase X]           # check + summary
    python scripts/config.py [config.toml] [--phase X] --json    # resolved config
    python scripts/config.py [config.toml] [--phase X] --shell   # for dashboard.sh
"""
import argparse
import json
import os
import re
import shlex
import sys
import tomllib

PHASE_NAMES = {
    "new": "新案審查", "amendment": "修正案審查", "re_review": "複審案審查",
    "continuing": "期中審查", "closure": "結案審查", "sae": "嚴重不良反應事件審查",
    "ib_update": "主持人手冊更新", "import": "專案進口審查",
    "suspension": "計畫暫停/提前終止", "appeal": "申覆案審查",
}

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

REQUIRED = [
    ("phase",), ("study", "title_zh"), ("study", "type"), ("study", "review_type"),
    ("pi", "name"), ("pi", "dept"), ("dates", "study_start"), ("dates", "study_end"),
    ("subjects", "planned_n"),
]

_CJK = r"　-〿一-鿿＀-￯"


class ConfigError(Exception):
    """Config cannot be loaded or is missing required fields."""


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
    if not any(l.strip() for l in lines):
        return ""
    starts = [l for l in lines if l.strip() and not l.startswith((" ", "\t"))]
    if starts and all(_ITEM.match(l) for l in starts):
        items = []
        for l in lines:
            m = _ITEM.match(l) if not l.startswith((" ", "\t")) else None
            if m:
                items.append([m.group(1)])
            elif l.strip():
                items[-1].append(l)  # continuation line
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
        body = "\n".join(l for l in text.splitlines() if not l.startswith("# "))
        return _block(body)
    return {_section_key(h): _block(b) for h, b in zip(parts[1::2], parts[2::2])}


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


def _missing(config):
    out = []
    for keys in REQUIRED:
        node = config
        for k in keys:
            node = node.get(k) if isinstance(node, dict) else None
        if node in (None, ""):
            out.append(".".join(keys))
    return out


def load_config(path="config.toml", phase=None):
    """Load config.toml, inline every @reference, apply a phase override."""
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise ConfigError(f"config not found: {path}")
    try:
        config = _resolve(_read(path), os.path.dirname(path), [path])
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"invalid TOML: {e}") from e
    if phase:
        config["phase"] = phase
    missing = _missing(config)
    if missing:
        raise ConfigError(f"{os.path.basename(path)}: missing required field(s): {', '.join(missing)}")
    if config["phase"] not in PHASE_NAMES:
        raise ConfigError(f"unknown phase {config['phase']!r}; expected one of: {', '.join(PHASE_NAMES)}")
    return config


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
