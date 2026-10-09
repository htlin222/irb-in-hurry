"""Submission dashboard: study summary, output counts, checklist status, file list.

Usage: irbh dashboard [config.toml] [--output DIR] [--phase PHASE]
"""
import glob
import os
import sys

from irb_in_hurry.config import ConfigError, load_config
from irb_in_hurry.form_selector import PHASE_NAMES
from irb_in_hurry.institution import resolve_id

COLORS = {"green": "\033[0;32m", "yellow": "\033[1;33m", "red": "\033[0;31m",
          "cyan": "\033[0;36m", "bold": "\033[1m", "off": "\033[0m"}
RULE = "═" * 46


def _painter(enabled):
    def paint(color, text):
        return f"{COLORS[color]}{text}{COLORS['off']}" if enabled else str(text)
    return paint


def _human_size(n):
    for unit in ("B", "K", "M", "G"):
        if n < 1024 or unit == "G":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024


def main(config_path="config.toml", output_dir="output", phase=None, checklist_path="checklist.md",
         color=None):
    """Print the dashboard. Returns a process exit code."""
    paint = _painter(sys.stdout.isatty() and not os.environ.get("NO_COLOR") if color is None else color)
    if not os.path.isfile(config_path):
        print(f"⚠ {config_path} not found")
        return 1
    try:
        config = load_config(config_path, phase)
    except ConfigError as e:
        print(f"⚠ Could not load {config_path}: {e}")
        return 1

    s = config["study"]
    bar = paint("bold", "║")

    def row(text=""):
        print(f"{bar} {text}")

    def sep():
        print(paint("bold", f"╠{RULE}╣"))

    print()
    print(paint("bold", f"╔{RULE}╗"))
    print(f"{paint('bold', '║')}     {paint('cyan', resolve_id(config).upper() + ' IRB Submission Dashboard')}")
    sep()
    row(f"IRB No:     {paint('green', s.get('irb_no') or '（待核發）')}")
    row(f"Phase:      {paint('cyan', PHASE_NAMES.get(config['phase'], config['phase']))} ({config['phase']})")
    row(f"PI:         {config['pi']['name']}")
    row(f"Study Type: {s['type']} / {s['review_type']}")
    row(f"Title:      {s['title_zh'][:40]}...")
    sep()

    docx = sorted(glob.glob(os.path.join(output_dir, "*.docx")))
    pdfs = glob.glob(os.path.join(output_dir, "*.pdf"))
    pngs = glob.glob(os.path.join(output_dir, "preview", "*.png"))
    for label, files in (("DOCX files:", docx), ("PDF files: ", pdfs), ("Previews:  ", pngs)):
        row(f"{paint('green', '■')} {label} {len(files)}")
    sep()

    if os.path.isfile(checklist_path):
        with open(checklist_path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        done = sum(1 for line in lines if line.startswith("■"))
        todo = [line for line in lines if line.startswith("□")]
        total = done + len(todo)
        if not todo and done:
            row(f"Checklist:  {paint('green', f'{done}/{total} complete ✓')}")
        elif todo:
            row(f"Checklist:  {paint('yellow', f'{done}/{total} complete ({len(todo)} pending)')}")
        sep()
        if todo:
            row(paint("yellow", "Pending:"))
            for line in todo:
                row(f"  {paint('red', line)}")
            sep()
    else:
        row(paint("red", "□ No checklist found. Run `irbh generate` first"))
        sep()

    if docx:
        row(paint("cyan", "Output Files:"))
        for path in docx:
            name, size = os.path.basename(path), _human_size(os.path.getsize(path))
            has_pdf = os.path.exists(os.path.splitext(path)[0] + ".pdf")
            mark = paint("green", "■") if has_pdf else paint("yellow", "■")
            status = paint("green", "✓ PDF") if has_pdf else paint("red", "□ PDF")
            row(f"  {mark} {name} ({size}) {status}")

    print(paint("bold", f"╚{RULE}╝"))
    print()
    return 0


if __name__ == "__main__":
    from irb_in_hurry.cli import main as cli
    sys.exit(cli(["dashboard", *sys.argv[1:]]))
