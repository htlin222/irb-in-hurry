#!/usr/bin/env python3
"""Main orchestrator: load config → select forms → generate all → update checklist."""
import os
import sys
import importlib

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.docx_utils import load_config
from scripts.form_selector import select_forms, get_generator, FORM_REGISTRY
from scripts.checklist import generate_checklist


def main(config_path="config.yml", output_dir="output"):
    """Generate all required IRB forms based on config."""
    config = load_config(config_path)
    os.makedirs(output_dir, exist_ok=True)

    # Phase name mapping
    phase_names = {
        "new": "新案審查", "amendment": "修正案審查", "re_review": "複審案審查",
        "continuing": "期中審查", "closure": "結案審查", "sae": "嚴重不良反應事件審查",
        "ib_update": "主持人手冊更新", "import": "專案進口審查",
        "suspension": "計畫暫停/提前終止", "appeal": "申覆案審查",
    }

    phase = config["phase"]
    phase_zh = phase_names.get(phase, phase)
    irb_no = config["study"]["irb_no"]

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
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yml"
    main(config_path)
