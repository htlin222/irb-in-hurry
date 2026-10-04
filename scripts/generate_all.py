#!/usr/bin/env python3
"""Main orchestrator: load config → select forms → generate all → update checklist."""
import os
import sys
import argparse
import glob
import importlib

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import load_config, ConfigError, PHASE_NAMES
from scripts.docx_utils import apply_official_page_setup
from scripts.form_selector import select_forms, get_generator, FORM_REGISTRY
from scripts.checklist import generate_checklist


def main(config_path="config.toml", output_dir="output", phase=None):
    """Generate all required IRB forms based on config."""
    try:
        config = load_config(config_path, phase)
    except ConfigError as e:
        sys.exit(f"✗ {e}")
    os.makedirs(output_dir, exist_ok=True)
    # output/ is disposable: drop the previous run so a phase switch leaves no strays
    for pattern in ("*.docx", "*.pdf", "preview/*.png", "preview/compare/*.png"):
        for f in glob.glob(os.path.join(output_dir, pattern)):
            os.remove(f)

    phase = config["phase"]
    phase_zh = PHASE_NAMES[phase]
    irb_no = config["study"]["irb_no"] or "（待核發）"

    print(f"╔══════════════════════════════════════════════╗")
    print(f"║  IRB-in-Hurry Form Generator                ║")
    print(f"╠══════════════════════════════════════════════╣")
    print(f"║  IRB No:  {irb_no:<34}║")
    print(f"║  Phase:   {phase_zh:<34}║")
    print(f"╚══════════════════════════════════════════════╝")
    print()

    # Select required forms
    forms = select_forms(config)
    print(f"Selected {len(forms)} forms for {phase_zh}:")
    for fid, name_zh in forms:
        print(f"  → {fid} {name_zh}")
    print()

    # Generate each form
    results = []  # (form_id, name_zh, path_or_None, status)
    for fid, name_zh in forms:
        gen_info = get_generator(fid)
        if gen_info is None:
            print(f"  ⚠ {fid} {name_zh} — no generator registered")
            results.append((fid, name_zh, None, "missing"))
            continue

        mod_path, func_name = gen_info
        try:
            mod = importlib.import_module(f"scripts.{mod_path}")
            gen_func = getattr(mod, func_name)
            path = gen_func(config, output_dir)
            apply_official_page_setup(path)
            print(f"  ■ {fid} {name_zh} → {os.path.basename(path)}")
            results.append((fid, name_zh, path, "generated"))
        except Exception as e:
            print(f"  ✗ {fid} {name_zh} — ERROR: {e}")
            results.append((fid, name_zh, None, "error"))

    # Generate checklist
    checklist_path = generate_checklist(config, results, phase_zh)
    print(f"\n■ Checklist written to {checklist_path}")

    # Summary
    generated = sum(1 for _, _, _, s in results if s == "generated")
    errors = sum(1 for _, _, _, s in results if s == "error")
    missing = sum(1 for _, _, _, s in results if s == "missing")
    print(f"\n{'═' * 46}")
    print(f"  Generated: {generated}  Errors: {errors}  Missing: {missing}")
    print(f"  Output:    {os.path.abspath(output_dir)}/")
    print(f"{'═' * 46}")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate IRB forms from config.toml")
    ap.add_argument("config", nargs="?", default="config.toml")
    ap.add_argument("--phase", default=os.environ.get("PHASE") or None,
                    help="override config phase without editing the file")
    ap.add_argument("--output", default="output")
    args = ap.parse_args()
    main(args.config, args.output, args.phase)
