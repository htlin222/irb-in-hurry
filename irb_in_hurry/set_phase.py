"""Persist `phase = "..."` in config.toml in place, keeping comments and formatting.

For a one-off run in another phase there is no need to edit the file:
`irbh closure` / `irbh all --phase closure` override it. Use this to make the
switch permanent.

Usage: irbh set-phase PHASE [config.toml]
"""
import re
import sys

from irb_in_hurry.form_selector import PHASE_FORMS

# Top-level `phase = ...`, capturing the value so a trailing comment survives.
PHASE_LINE = re.compile(r'^(phase\s*=\s*)("[^"\n]*"|\'[^\'\n]*\'|[^\s#]+)', re.M)
TABLE_HEADER = re.compile(r"^\s*\[", re.M)


def set_phase(path, phase):
    if phase not in PHASE_FORMS:
        raise ValueError(f"Unknown phase {phase!r}. Valid: {', '.join(PHASE_FORMS)}")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # Only keys before the first [table] header are top-level.
    header = TABLE_HEADER.search(text)
    top_end = header.start() if header else len(text)
    top, rest = text[:top_end], text[top_end:]
    top, n = PHASE_LINE.subn(lambda m: f'{m.group(1)}"{phase}"', top, count=1)
    if n == 0:
        line = f'phase = "{phase}"\n'
        top = line + "\n" + top if header else top.rstrip("\n") + ("\n\n" if top.strip() else "") + line
    with open(path, "w", encoding="utf-8") as f:
        f.write(top + rest)


if __name__ == "__main__":
    from irb_in_hurry.cli import main as cli
    sys.exit(cli(["set-phase", *sys.argv[1:]]))
