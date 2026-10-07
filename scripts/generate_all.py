#!/usr/bin/env python3
"""Main orchestrator: load config → select forms → generate all → update checklist.

Usage: uv run python scripts/generate_all.py [config.toml] [--output DIR] [--phase PHASE]

--phase (or the PHASE environment variable) overrides `phase` for one run
without editing config.toml.
"""
import argparse
import glob
import os
import sys
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.checklist import generate_checklist
from scripts.config import ConfigError, load_config
from scripts.docx_utils import apply_official_page_setup
from scripts.form_selector import PHASE_NAMES, get_generator, load_generator, select_forms
from scripts.institution import activate


def generate_form(form_id, config, output_dir):
    """Run one form's generator and normalize its page setup. Returns the DOCX path."""
    path = load_generator(form_id)(config, output_dir)
    apply_official_page_setup(path)
    return path


def main(config_path="config.toml", output_dir="output", phase=None, verbose=False,
         checklist_path="checklist.md"):
    """Generate all required IRB forms based on config. Returns a process exit code."""
    if not os.path.isfile(config_path):
        print(f"✗ {config_path} not found — start from an example: make init EXAMPLE=<name>")
        return 2
    try:
        config = load_config(config_path, phase)
    except ConfigError as e:
        print(f"✗ {e}")
        return 2
    inst = activate(config)
    os.makedirs(output_dir, exist_ok=True)
    # output/ is disposable: drop the previous run so a phase switch leaves no
    # stray forms to be converted, validated and reviewed as if they were current.
    for pattern in ("*.docx", "*.pdf", "preview/*.png", "preview/compare/*.png"):
        for f in glob.glob(os.path.join(output_dir, pattern)):
            os.remove(f)

    phase = config["phase"]
    phase_zh = PHASE_NAMES.get(phase, phase)
    irb_no = config["study"]["irb_no"] or "（待核發）"

    print("╔══════════════════════════════════════════════╗")
    print("║  IRB-in-Hurry Form Generator                 ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"  IRB:     {inst.id}")
    print(f"  IRB No:  {irb_no}")
    print(f"  Phase:   {phase_zh} ({phase})")
    print("╚══════════════════════════════════════════════╝")
    print()

    forms = select_forms(config)
    print(f"Selected {len(forms)} forms for {phase_zh}:")
    for fid, name_zh in forms:
        print(f"  → {fid} {name_zh}")
    print()

    results = []  # (form_id, name_zh, path_or_None, status)
    for fid, name_zh in forms:
        if get_generator(fid) is None:
            print(f"  ⚠ {fid} {name_zh} — no generator registered")
            results.append((fid, name_zh, None, "missing"))
            continue
        try:
            path = generate_form(fid, config, output_dir)
        except Exception as e:
            print(f"  ✗ {fid} {name_zh} — ERROR: {type(e).__name__}: {e}")
            if verbose:
                traceback.print_exc()
            results.append((fid, name_zh, None, "error"))
            continue
        print(f"  ■ {fid} {name_zh} → {os.path.basename(path)}")
        results.append((fid, name_zh, path, "generated"))

    generate_checklist(config, results, phase_zh, checklist_path)

    print(f"\n■ Checklist written to {checklist_path}")

    generated = sum(1 for *_, s in results if s == "generated")
    errors = sum(1 for *_, s in results if s == "error")
    missing = sum(1 for *_, s in results if s == "missing")
    print(f"\n{'═' * 46}")
    print(f"  Generated: {generated}  Errors: {errors}  Missing: {missing}")
    print(f"  Output:    {os.path.abspath(output_dir)}/")
    if errors and not verbose:
        print("  Re-run with --verbose for full tracebacks")
    print(f"{'═' * 46}")
    return 1 if errors else 0


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Generate IRB forms from config.toml")
    parser.add_argument("config", nargs="?", default="config.toml", help="study config (default: config.toml)")
    parser.add_argument("-o", "--output", default="output", help="output directory (default: output)")
    parser.add_argument("--phase", choices=list(PHASE_NAMES), default=os.environ.get("PHASE") or None,
                        help="override `phase` from the config without editing it (default: $PHASE)")
    parser.add_argument("-v", "--verbose", action="store_true", help="print tracebacks for failed forms")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.config, args.output, args.phase, args.verbose))
