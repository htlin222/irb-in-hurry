"""`irbh` — the IRB-in-Hurry command line.

Run it in a study folder (config.toml + cv.toml + 中文計畫摘要.md):

    irbh init gcsf-retrospective   # start from a bundled example (+ Claude Code skill)
    irbh check                     # resolve @references + validate config.toml
    irbh templates                 # once: cache the institution's blank forms
    irbh all                       # generate + PDF + layout gate + dashboard
    irbh closure                   # = irbh all --phase closure (config.toml untouched)
    irbh set-phase closure         # persist the phase in config.toml (keeps comments)
    irbh onboard myhosp            # new institution: blanks in templates/myhosp/ → draft pack
    irbh doctor                    # check LibreOffice, poppler, fonts, config, blanks

`--phase` defaults to $PHASE, so `PHASE=closure irbh all` works too.
"""
import argparse
import os
import shutil
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version

from irb_in_hurry import institution
from irb_in_hurry.form_selector import PHASE_NAMES

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLES_DIR = os.path.join(PACKAGE_DIR, "examples")
SKILL_DEST = os.path.join(".claude", "skills", "irb")
STUDY_GITIGNORE = """\
# IRB-in-Hurry: generated files and the institution's blank forms
output/
checklist.md
reviewers/
templates/
"""


def package_version():
    try:
        return version("irb-in-hurry")
    except PackageNotFoundError:
        return "0+unknown"


def skill_source():
    """The bundled Claude Code skill: inside the wheel, or .claude/skills/irb in a source checkout."""
    for path in (os.path.join(PACKAGE_DIR, "skill"),
                 os.path.join(os.path.dirname(PACKAGE_DIR), ".claude", "skills", "irb")):
        if os.path.isfile(os.path.join(path, "SKILL.md")):
            return path
    return None


def examples():
    return sorted(d for d in os.listdir(EXAMPLES_DIR) if os.path.isfile(os.path.join(EXAMPLES_DIR, d, "config.toml")))


# ── commands ────────────────────────────────────────────────────────────────

def cmd_init(args):
    if not args.example:
        print("Bundled examples (irbh init <name>):")
        for name in examples():
            print(f"  {name}")
        return 0
    src = os.path.join(EXAMPLES_DIR, args.example)
    if args.example not in examples():
        print(f"✗ no example '{args.example}' (have: {', '.join(examples())})")
        return 2
    files = sorted(os.listdir(src))
    clashes = [f for f in files if os.path.exists(f)]
    if clashes and not args.force:
        print(f"✗ {', '.join(clashes)} already exist here (--force to overwrite)")
        return 1
    for f in files:
        shutil.copyfile(os.path.join(src, f), f)
        print(f"  ■ {f}")
    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w", encoding="utf-8") as fh:
            fh.write(STUDY_GITIGNORE)
        print("  ■ .gitignore")
    if not args.no_skill:
        install_skill(force=False)
    from irb_in_hurry import config
    return config.main(["config.toml"])


def install_skill(force=False, dest=SKILL_DEST):
    src = skill_source()
    if src is None:
        print("⚠ Claude Code skill not bundled with this install — skipped")
        return 1
    if os.path.exists(dest):
        if os.path.samefile(src, dest) or not force:
            print(f"  · keep {dest}/ (exists; `irbh skill --force` to update)")
            return 0
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    print(f"  ■ {dest}/ (Claude Code skill — open this folder in Claude Code and ask it to fill the forms)")
    return 0


def cmd_skill(args):
    return install_skill(force=args.force)


def cmd_check(args):
    from irb_in_hurry import config
    argv = [args.config] + (["--phase", args.phase] if args.phase else [])
    argv += ["--json"] if args.json else ["--shell"] if args.shell else []
    return config.main(argv)


def cmd_generate(args):
    from irb_in_hurry import generate_all
    return generate_all.main(args.config, args.output, args.phase, args.verbose)


def cmd_pdf(args):
    from irb_in_hurry import convert
    return convert.main(args.output)


def cmd_templates(args):
    from irb_in_hurry import fetch_templates
    _activate(args.config)
    return fetch_templates.main(force=args.force) or 0


def cmd_onboard(args):
    from irb_in_hurry import onboard
    return onboard.main(args.id, force=args.force)


def cmd_validate(args):
    from irb_in_hurry import validate_layout
    _activate(args.config)
    return validate_layout.main(args.output, render=not args.no_render, strict=args.strict)


def cmd_dashboard(args):
    from irb_in_hurry import dashboard
    return dashboard.main(args.config, args.output, args.phase)


def cmd_all(args):
    args.no_render = args.strict = False
    for step in (cmd_generate, cmd_pdf, cmd_validate, cmd_dashboard):
        code = step(args)
        if code:
            return code
    return 0


def cmd_review(args):
    from irb_in_hurry.config import ConfigError
    from irb_in_hurry.reviewer import run_review
    try:
        return 0 if run_review(args.config, args.output, phase=args.phase) else 1
    except (ConfigError, FileNotFoundError) as e:
        print(f"✗ {e}")
        return 1


def cmd_set_phase(args):
    from irb_in_hurry.set_phase import set_phase
    try:
        set_phase(args.config, args.phase)
    except (OSError, ValueError) as e:
        print(f"✗ {e}")
        return 1
    print(f"■ phase → {args.phase}")
    return 0


def cmd_institutions(args):
    active = institution.resolve_id()
    print("Institution packs (first match wins: local → installed → bundled):")
    for inst_id, (pack_dir, source) in sorted(institution.available().items()):
        mark = "■" if inst_id == active else " "
        print(f"  {mark} {inst_id:<12} {source:<9} {pack_dir}")
    return 0


def cmd_doctor(args):
    from irb_in_hurry.config import ConfigError, load_config
    from irb_in_hurry.convert import find_soffice

    problems = warnings = 0

    def report(ok, label, detail, required=True):
        nonlocal problems, warnings
        mark = "■" if ok else ("✗" if required else "⚠")
        problems += not ok and required
        warnings += not ok and not required
        print(f"  {mark} {label:<14} {detail}")

    print(f"irb-in-hurry {package_version()} · Python {sys.version.split()[0]} · {sys.platform}")
    soffice = find_soffice()
    report(bool(soffice), "LibreOffice", soffice or "missing — needed for PDF + layout gate "
           "(brew install --cask libreoffice / winget install TheDocumentFoundation.LibreOffice / apt install libreoffice)")
    pdftoppm = shutil.which("pdftoppm")
    report(bool(pdftoppm), "poppler", pdftoppm or "missing — PNG previews only (brew install poppler / apt install poppler-utils)",
           required=False)

    config = None
    if os.path.isfile(args.config):
        try:
            config = load_config(args.config)
            report(True, "config", f"{args.config} OK (phase {config['phase']})")
        except ConfigError as e:
            report(False, "config", str(e).splitlines()[0])
    else:
        report(False, "config", f"no {args.config} here — `irbh init <example>` to start", required=False)

    try:
        prof = institution.load(institution.resolve_id(config))
    except FileNotFoundError as e:
        report(False, "institution", str(e))
        return 1
    report(True, "institution", f"{prof.id} ({prof.source}: {prof.dir})")
    cached = os.path.isfile(os.path.join(prof.template_dir, "index.json"))
    report(cached, "blank forms", os.path.relpath(prof.template_dir) if cached else
           f"not cached in {os.path.relpath(prof.template_dir)}/ — run `irbh templates`", required=False)

    font = prof.font["name"]
    if shutil.which("fc-match"):
        names = sorted(prof.font_aliases)
        env = None
        if sys.platform.startswith("linux"):
            from irb_in_hurry.convert import soffice_env
            env = soffice_env()
        matched = subprocess.run(["fc-match", "-f", "%{family}", font], capture_output=True, text=True,
                                 env=env).stdout.strip()
        exact = any(n in matched for n in names) or "Kai" in matched
        report(exact, "form font", f"{font} → {matched or '?'}" + ("" if exact else
               " (PDF renders will substitute; install the font or fonts-arphic-ukai on Linux)"), required=False)
    else:
        report(True, "form font", f"{font} (fc-match unavailable; check Word shows {font})")
    if problems:
        print(f"\n{problems} problem(s) to fix before `irbh all`.")
    else:
        print("\nAll set." + (f" ({warnings} warning(s) above are optional.)" if warnings else ""))
    return 1 if problems else 0


def _activate(config_path):
    """Pick the institution named in the study's config (for commands that don't load it themselves)."""
    from irb_in_hurry.config import ConfigError, load_config
    if os.path.isfile(config_path):
        try:
            institution.activate(load_config(config_path))
        except ConfigError:
            pass


# ── parser ──────────────────────────────────────────────────────────────────

def build_parser():
    env_phase = os.environ.get("PHASE") or None
    ap = argparse.ArgumentParser(prog="irbh", description="IRB-in-Hurry: study facts → official IRB forms → PDF.",
                                 epilog="Phase shortcut: `irbh <phase>` = `irbh all --phase <phase>` "
                                        f"({', '.join(PHASE_NAMES)}).")
    ap.add_argument("-V", "--version", action="version", version=f"irb-in-hurry {package_version()}")
    ap.add_argument("-C", "--dir", metavar="DIR", help="run in this study folder instead of the current one")
    sub = ap.add_subparsers(dest="command", metavar="<command>")

    def command(name, func, help, *, config=False, output=False, phase=False):
        p = sub.add_parser(name, help=help, description=help)
        p.set_defaults(func=func)
        if config:
            p.add_argument("config", nargs="?", default="config.toml", help="study config (default: config.toml)")
        if output:
            p.add_argument("-o", "--output", default="output", help="output folder (default: output)")
        if phase:
            p.add_argument("--phase", choices=list(PHASE_NAMES), default=env_phase,
                           help="override `phase` for this run without editing config.toml (default: $PHASE)")
        return p

    p = command("init", cmd_init, "start a study here from a bundled example (no name: list them)")
    p.add_argument("example", nargs="?")
    p.add_argument("--force", action="store_true", help="overwrite existing files")
    p.add_argument("--no-skill", action="store_true", help="don't install the Claude Code skill")

    p = command("check", cmd_check, "resolve @references in config.toml and validate it", config=True, phase=True)
    fmt = p.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", help="print the resolved config")
    fmt.add_argument("--shell", action="store_true", help="print shell variables")

    p = command("generate", cmd_generate, "generate the phase's DOCX forms", config=True, output=True, phase=True)
    p.add_argument("-v", "--verbose", action="store_true", help="print tracebacks for failed forms")

    command("pdf", cmd_pdf, "convert output DOCX → PDF + PNG previews (LibreOffice)", output=True)

    p = command("templates", cmd_templates, "cache the institution's official blank forms", config=True)
    p.add_argument("--force", action="store_true", help="re-download cached blanks")

    p = command("onboard", cmd_onboard, "draft institutions/<id>/ from the blank forms in templates/<id>/")
    p.add_argument("id")
    p.add_argument("--force", action="store_true", help="overwrite an existing draft")

    p = command("validate", cmd_validate, "layout/font gate against the blank forms", config=True, output=True)
    p.add_argument("--no-render", action="store_true", help="skip the LibreOffice render checks")
    p.add_argument("--strict", action="store_true", help="fail on warnings too")

    p = command("all", cmd_all, "generate + pdf + validate + dashboard", config=True, output=True, phase=True)
    p.add_argument("-v", "--verbose", action="store_true", help="print tracebacks for failed forms")

    command("dashboard", cmd_dashboard, "show submission status", config=True, output=True, phase=True)
    command("review", cmd_review, "simulated IRB reviewer on the generated forms", config=True, output=True,
            phase=True)

    p = command("set-phase", cmd_set_phase, "persist `phase` in config.toml (keeps comments)")
    p.add_argument("phase", choices=list(PHASE_NAMES))
    p.add_argument("config", nargs="?", default="config.toml")

    command("institutions", cmd_institutions, "list institution packs and which one is active")

    p = command("skill", cmd_skill, f"install the Claude Code skill into {SKILL_DEST}/")
    p.add_argument("--force", action="store_true", help="replace an existing copy")

    command("doctor", cmd_doctor, "check LibreOffice, poppler, font, config and blank forms", config=True)
    return ap


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # `irbh closure …` → `irbh all --phase closure …` (after any global -C DIR)
    i = 2 if argv[:1] in (["-C"], ["--dir"]) else 0
    if len(argv) > i and argv[i] in PHASE_NAMES:
        argv[i:i + 1] = ["all", "--phase", argv[i]]
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.dir:
        os.chdir(args.dir)
    if not args.command:
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
