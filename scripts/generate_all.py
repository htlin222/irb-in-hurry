#!/usr/bin/env python3
"""Main orchestrator: load config → select forms → generate all → update checklist.

Usage: uv run python scripts/generate_all.py [config.yml] [--output DIR] [--phase PHASE]
"""
import argparse
import glob
import importlib
import os
import sys
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.checklist import generate_checklist
from scripts.config import ConfigError, load_config
from scripts.docx_utils import apply_official_page_setup
from scripts.form_selector import PHASE_FORMS, PHASE_NAMES, get_generator, select_forms


def generate_form(form_id, config, output_dir):
    """Run one form's generator and normalize its page setup. Returns the DOCX path."""
    mod_path, func_name = get_generator(form_id)
    gen_func = getattr(importlib.import_module(f"scripts.{mod_path}"), func_name)
    path = gen_func(config, output_dir)
    apply_official_page_setup(path)
    return path


def main(config_path="config.yml", output_dir="output", phase=None, verbose=False,
         checklist_path="checklist.md"):
    """Generate all required IRB forms based on config. Returns a process exit code."""
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print(f"✗ {config_path} not found — copy a fixture from tests/fixtures/ to start")
        return 2
    except ConfigError as e:
        print(f"✗ {e}")
        return 2
    if phase:
        config["phase"] = phase
    os.makedirs(output_dir, exist_ok=True)

    phase = config["phase"]
    phase_zh = PHASE_NAMES.get(phase, phase)
    irb_no = config["study"]["irb_no"] or "（尚未取得）"

    print("╔══════════════════════════════════════════════╗")
    print("║  IRB-in-Hurry Form Generator                 ║")
    print("╠══════════════════════════════════════════════╣")
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

    # Forms left over from an earlier run (e.g. another phase) would otherwise
    # be converted, validated and reviewed as if they belonged to this one.
    fresh = {os.path.abspath(p) for _, _, p, _ in results if p}
    stale = sorted(os.path.basename(p) for p in glob.glob(os.path.join(output_dir, "*.docx"))
                   if os.path.abspath(p) not in fresh)
    if stale:
        print(f"\n⚠ {len(stale)} DOCX in {output_dir}/ not produced by this run (run `make clean` to drop):")
        for name in stale:
            print(f"    {name}")
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
    parser = argparse.ArgumentParser(description="Generate KFSYSCC IRB forms from config.yml")
    parser.add_argument("config", nargs="?", default="config.yml", help="study config (default: config.yml)")
    parser.add_argument("-o", "--output", default="output", help="output directory (default: output)")
    parser.add_argument("--phase", choices=list(PHASE_FORMS), help="override `phase` from the config")
    parser.add_argument("-v", "--verbose", action="store_true", help="print tracebacks for failed forms")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.config, args.output, args.phase, args.verbose))
