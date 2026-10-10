"""`irbh` CLI and installed-package behaviour: everything runs from a study folder, not the repo."""
import os
import sys

import pytest

from irb_in_hurry import cli, institution
from tests.test_institution import make_blank


@pytest.fixture
def study(tmp_path, monkeypatch):
    """An empty study folder as the working directory, with no institution forced."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(institution.ENV_VAR, raising=False)
    monkeypatch.delenv(institution.TEMPLATES_ENV, raising=False)
    monkeypatch.delenv("PHASE", raising=False)
    return tmp_path


def test_init_lists_and_copies_examples(study, capsys):
    assert cli.main(["init"]) == 0
    assert "gcsf-retrospective" in capsys.readouterr().out

    assert cli.main(["init", "gcsf-retrospective", "--no-skill"]) == 0
    assert (study / "config.toml").is_file() and (study / "cv.toml").is_file()
    assert "templates/" in (study / ".gitignore").read_text()
    # never clobbers a study in progress
    assert cli.main(["init", "gcsf-retrospective", "--no-skill"]) == 1
    assert cli.main(["init", "no-such-example"]) == 2


def test_init_installs_skill(study):
    assert cli.main(["init", "gcsf-retrospective"]) == 0
    assert (study / ".claude" / "skills" / "irb" / "SKILL.md").is_file()


def test_generate_and_phase_shortcut(study):
    cli.main(["init", "gcsf-retrospective", "--no-skill"])
    assert cli.main(["generate"]) == 0
    assert any(f.endswith(".docx") for f in os.listdir(study / "output"))
    assert (study / "checklist.md").is_file()

    # `irbh closure` runs the closure phase without editing config.toml
    before = (study / "config.toml").read_text(encoding="utf-8")
    args = cli.build_parser().parse_args(["all", "--phase", "closure"])
    assert args.phase == "closure"
    assert cli.main(["generate", "--phase", "closure"]) == 0
    assert (study / "config.toml").read_text(encoding="utf-8") == before
    assert "結案" in (study / "checklist.md").read_text(encoding="utf-8")


def test_phase_shortcut_rewrites_argv(monkeypatch):
    seen = {}
    monkeypatch.setattr(cli, "cmd_all", lambda args: seen.update(vars(args)) or 0)
    assert cli.main(["closure", "-o", "out"]) == 0
    assert seen["phase"] == "closure" and seen["output"] == "out"


def test_dir_option_and_set_phase(study, tmp_path_factory):
    other = tmp_path_factory.mktemp("other")
    assert cli.main(["-C", str(other), "init", "gcsf-retrospective", "--no-skill"]) == 0
    assert cli.main(["set-phase", "closure"]) == 0  # cwd is now `other`
    assert 'phase = "closure"' in (other / "config.toml").read_text(encoding="utf-8")


def test_dashboard_and_check(study, capsys):
    cli.main(["init", "gcsf-retrospective", "--no-skill"])
    cli.main(["generate"])
    capsys.readouterr()
    assert cli.main(["dashboard"]) == 0
    out = capsys.readouterr().out
    assert "KFSYSCC IRB Submission Dashboard" in out and "DOCX files:" in out
    assert cli.main(["check", "--shell"]) == 0
    assert "PHASE=new" in capsys.readouterr().out


def test_bundled_pack_is_found_outside_the_repo(study, capsys):
    prof = institution.load("kfsyscc")
    assert prof.source in ("installed", "bundled")
    assert os.path.isfile(os.path.join(prof.dir, "profile.toml"))
    # blanks are looked up in the study folder, not inside the package
    assert prof.template_dir == os.path.join(str(study), "templates", "kfsyscc")
    assert cli.main(["institutions"]) == 0
    assert "kfsyscc" in capsys.readouterr().out


def test_shared_template_cache(study, monkeypatch, tmp_path_factory):
    shared = tmp_path_factory.mktemp("blanks")
    monkeypatch.setenv(institution.TEMPLATES_ENV, str(shared))
    assert institution.load("kfsyscc").template_dir == os.path.join(str(shared), "kfsyscc")


def test_local_pack_from_onboard_generates(study, monkeypatch):
    """onboard → institutions/<id>/ in the study folder → selectable and importable."""
    tpl = study / "templates" / "demo"
    tpl.mkdir(parents=True)
    make_blank(tpl / "IRB-F1 新案申請書.docx")
    assert cli.main(["onboard", "demo"]) == 0
    assert institution.available()["demo"][1] == "local"

    cli.main(["init", "gcsf-retrospective", "--no-skill"])
    cfg = (study / "config.toml").read_text(encoding="utf-8")
    (study / "config.toml").write_text(cfg.replace('institution = "kfsyscc"', 'institution = "demo"'),
                                       encoding="utf-8")
    monkeypatch.setattr(sys, "path", list(sys.path))
    for mod in [m for m in sys.modules if m == "institutions" or m.startswith("institutions.")]:
        monkeypatch.delitem(sys.modules, mod)
    try:
        assert cli.main(["generate"]) == 0
        assert (study / "output").is_dir() and os.listdir(study / "output")
    finally:
        os.environ.pop(institution.ENV_VAR, None)


def test_local_pack_overrides_bundled(study):
    local = study / "institutions" / "kfsyscc"
    local.mkdir(parents=True)
    (local / "profile.toml").write_text(
        'id = "kfsyscc"\nname = "本地測試"\nforms_module = "institutions.kfsyscc.forms"\n'
        '[page]\nwidth = 1\nheight = 1\n[font]\nname = "標楷體"\n', encoding="utf-8")
    prof = institution.load("kfsyscc")
    assert prof.source == "local" and prof.name == "本地測試"


def test_doctor_runs(study, capsys):
    cli.main(["init", "gcsf-retrospective", "--no-skill"])
    capsys.readouterr()
    cli.main(["doctor"])
    out = capsys.readouterr().out
    assert "LibreOffice" in out and "institution" in out and "config.toml OK" in out
