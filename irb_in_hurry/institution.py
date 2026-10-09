"""Active institution profile (<pack>/profile.toml).

Everything that differs between IRBs — committee name, IRB-number label,
submission address, where the blank forms live, page setup, form font, and
which forms exist — is read from the profile, never hardcoded in the code.

Resolution order: IRB_INSTITUTION env var → `institution` in config.toml →
DEFAULT_INSTITUTION.

A pack `<id>` is looked up, first match wins, in:

  1. institutions/<id>/ in the study folder (what `irbh onboard` writes)
  2. an installed package registered under the `irb_in_hurry.institutions`
     entry-point group (name = id, value = the package holding profile.toml)
  3. the packs bundled with irb-in-hurry (irb_in_hurry/institutions/<id>/)

The study folder is the current working directory (`irbh -C DIR` changes it).
Blank forms live in templates/<id>/ there, or under $IRB_TEMPLATES/<id>/ to
share one cache between studies.
"""
import os
import re
import sys
import tomllib
from functools import lru_cache
from importlib.metadata import entry_points

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLED_DIR = os.path.join(PACKAGE_DIR, "institutions")
LOCAL_DIR = "institutions"
ENTRY_POINT_GROUP = "irb_in_hurry.institutions"
DEFAULT_INSTITUTION = "kfsyscc"
ENV_VAR = "IRB_INSTITUTION"
TEMPLATES_ENV = "IRB_TEMPLATES"


def project_root():
    """The study folder: config.toml, institutions/, templates/, output/ live here."""
    return os.getcwd()


class Profile:
    """Read-only view over profile.toml with derived conveniences."""

    def __init__(self, data, pack_dir=None, source="bundled"):
        self.data = data
        self.dir = pack_dir
        self.source = source
        self.id = data["id"]
        self.name = data["name"]
        self.committee = data.get("committee", "")
        self.irb_no_label = data.get("irb_no_label", "IRB編號")
        self.ehr_name = data.get("ehr_name", f"{self.name}電子病歷系統")
        self.forms_module = data["forms_module"]
        self.submission = data.get("submission", {})
        self.templates = data.get("templates", {})
        self.page = data["page"]
        self.font = data["font"]

    @property
    def heading(self):
        """Title line printed above every form, e.g. '某某醫院 人體試驗委員會'."""
        return f"{self.name} {self.committee}".strip()

    @property
    def submission_email(self):
        return self.submission.get("email", "")

    @property
    def template_dir(self):
        shared = os.environ.get(TEMPLATES_ENV)
        if shared:
            return os.path.join(os.path.abspath(shared), self.id)
        return os.path.join(project_root(), self.templates.get("dir", f"templates/{self.id}"))

    def blank_path(self, form_id):
        """Official blank DOCX for a form: templates.files mapping, else <id>.docx."""
        name = self.templates.get("files", {}).get(form_id, f"{form_id}.docx")
        return os.path.join(self.template_dir, name)

    @property
    def font_aliases(self):
        return {self.font["name"], *self.font.get("aliases", [])}

    def form_id(self, text):
        """Normalize a filename/link label to a form id, or None."""
        m = re.search(self.templates.get("form_id_pattern", r"$^"), text)
        if m:
            return self.templates.get("form_id_format", "{}").format(int(m.group(1)))
        for name, fid in self.templates.get("named_forms", {}).items():
            if name in text or fid.lower() in text.lower():
                return fid
        return None


def _id_from_config_file(path=None):
    path = path or os.path.join(project_root(), "config.toml")
    try:
        with open(path, "rb") as f:
            return tomllib.load(f).get("institution")
    except (OSError, tomllib.TOMLDecodeError):
        return None


def resolve_id(config=None):
    return (os.environ.get(ENV_VAR)
            or (config or {}).get("institution")
            or _id_from_config_file()
            or DEFAULT_INSTITUTION)


def _packs_in(folder):
    if not os.path.isdir(folder):
        return {}
    return {d: os.path.join(folder, d) for d in sorted(os.listdir(folder))
            if os.path.isfile(os.path.join(folder, d, "profile.toml"))}


def _installed_packs():
    packs = {}
    for ep in entry_points(group=ENTRY_POINT_GROUP):
        try:
            module = ep.load()
        except Exception as e:  # a broken third-party pack must not break the others
            print(f"⚠ institution pack '{ep.name}' ({ep.value}) failed to load: {e}", file=sys.stderr)
            continue
        pack_dir = os.path.dirname(os.path.abspath(module.__file__))
        if os.path.isfile(os.path.join(pack_dir, "profile.toml")):
            packs[ep.name] = pack_dir
    return packs


def available(root=None):
    """{id: (pack_dir, source)} for every pack visible from the study folder, highest priority first."""
    found = {}
    sources = (("local", _packs_in(os.path.join(root or project_root(), LOCAL_DIR))),
               ("installed", _installed_packs()),
               ("bundled", _packs_in(BUNDLED_DIR)))
    for source, packs in sources:
        for inst_id, pack_dir in packs.items():
            found.setdefault(inst_id, (pack_dir, source))
    return found


def load(inst_id):
    return _load(inst_id, project_root())


@lru_cache(maxsize=None)
def _load(inst_id, root):
    packs = available(root)
    if inst_id not in packs:
        raise FileNotFoundError(f"No institution profile '{inst_id}' (have: {', '.join(sorted(packs))})")
    pack_dir, source = packs[inst_id]
    if source == "local" and root not in sys.path:
        # Local packs are imported as `institutions.<id>.forms` from the study folder.
        sys.path.append(root)
    with open(os.path.join(pack_dir, "profile.toml"), "rb") as f:
        return Profile(tomllib.load(f), pack_dir, source)


def current():
    return load(resolve_id())


def activate(config):
    """Make config's `institution` the active profile for this process."""
    if not os.environ.get(ENV_VAR):
        os.environ[ENV_VAR] = resolve_id(config)
    return current()
