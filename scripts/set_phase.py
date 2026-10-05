#!/usr/bin/env python3
"""Switch `phase:` in config.yml in place, keeping comments and formatting.

Usage: uv run python scripts/set_phase.py PHASE [config.yml]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.form_selector import PHASE_FORMS

PHASE_LINE = re.compile(r"^phase:[^\n]*$", re.M)


def set_phase(path, phase):
    if phase not in PHASE_FORMS:
        raise ValueError(f"Unknown phase {phase!r}. Valid: {', '.join(PHASE_FORMS)}")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text, n = PHASE_LINE.subn(f"phase: {phase}", text, count=1)
    if n == 0:
        text = text.rstrip("\n") + f"\n\nphase: {phase}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[-1])
    try:
        set_phase(sys.argv[2] if len(sys.argv) > 2 else "config.yml", sys.argv[1])
    except (OSError, ValueError) as e:
        sys.exit(f"✗ {e}")
    print(f"■ phase → {sys.argv[1]}")
