"""Active institution profile (institutions/<id>/profile.yml).

Everything that differs between IRBs — committee name, IRB-number label,
submission address, where the blank forms live, page setup, form font, and
which forms exist — is read from the profile, never hardcoded in scripts.

Resolution order: IRB_INSTITUTION env var → `institution:` in config.yml →
DEFAULT_INSTITUTION.
"""
import os
import re
from functools import lru_cache

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTITUTIONS_DIR = os.path.join(ROOT, "institutions")
DEFAULT_INSTITUTION = "kfsyscc"
ENV_VAR = "IRB_INSTITUTION"


class Profile:
    """Read-only view over profile.yml with derived conveniences."""

    def __init__(self, data):
        self.data = data
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
        return os.path.join(ROOT, self.templates.get("dir", f"templates/{self.id}"))

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
    path = path or os.path.join(ROOT, "config.yml")
    try:
        with open(path, encoding="utf-8") as f:
            return (yaml.safe_load(f) or {}).get("institution")
    except OSError:
        return None


def resolve_id(config=None):
    return (os.environ.get(ENV_VAR)
            or (config or {}).get("institution")
            or _id_from_config_file()
            or DEFAULT_INSTITUTION)


@lru_cache(maxsize=None)
def load(inst_id):
    path = os.path.join(INSTITUTIONS_DIR, inst_id, "profile.yml")
    if not os.path.exists(path):
        known = sorted(d for d in os.listdir(INSTITUTIONS_DIR)
                       if os.path.exists(os.path.join(INSTITUTIONS_DIR, d, "profile.yml")))
        raise FileNotFoundError(f"No institution profile '{inst_id}' (have: {', '.join(known)})")
    with open(path, encoding="utf-8") as f:
        return Profile(yaml.safe_load(f))


def current():
    return load(resolve_id())


def activate(config):
    """Make config's `institution:` the active profile for this process."""
    if not os.environ.get(ENV_VAR):
        os.environ[ENV_VAR] = resolve_id(config)
    return current()
