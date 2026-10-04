"""Form selector: maps (study type + phase) → required IRB forms.

Institution-agnostic: the form registry and phase routing come from the active
institution's `forms_module` (see institutions/<id>/profile.yml).
"""
import importlib

from scripts.institution import current



def _pack():
    return importlib.import_module(current().forms_module)


def __getattr__(name):
    # FORM_REGISTRY / PHASE_FORMS of the active institution
    if name in ("FORM_REGISTRY", "PHASE_FORMS"):
        return getattr(_pack(), name)
    raise AttributeError(name)


# Auto-infer settings for retrospective studies
def _apply_study_type_defaults(config):
    """Auto-set fields based on study type."""
    if config["study"].get("type") == "retrospective":
        config["subjects"]["consent_waiver"] = True
        if not config["study"].get("review_type"):
            config["study"]["review_type"] = "expedited"
    return config


def select_forms(config):
    """Select required forms based on config.

    Returns: list of (form_id, form_name_zh) tuples in submission order.
    """
    config = _apply_study_type_defaults(config)
    phase = config["phase"]

    pack = _pack()
    PHASE_FORMS, FORM_REGISTRY = pack.PHASE_FORMS, pack.FORM_REGISTRY
    if phase not in PHASE_FORMS:
        raise ValueError(f"Unknown phase: {phase}. Valid: {list(PHASE_FORMS.keys())}")

    rules = PHASE_FORMS[phase]
    selected = list(rules["base"])

    for condition_fn, form_ids in rules["conditions"]:
        try:
            if condition_fn(config):
                for fid in form_ids:
                    if fid not in selected:
                        selected.append(fid)
        except (KeyError, TypeError):
            pass  # skip conditions that reference missing config keys

    result = []
    for fid in selected:
        if fid in FORM_REGISTRY:
            name_zh = FORM_REGISTRY[fid][0]
            result.append((fid, name_zh))
        else:
            result.append((fid, fid))

    return result


def get_generator(form_id):
    """Get (module_path, function_name) for a form ID."""
    FORM_REGISTRY = _pack().FORM_REGISTRY
    if form_id not in FORM_REGISTRY:
        return None
    _, mod_path, func_name = FORM_REGISTRY[form_id]
    return mod_path, func_name


def load_generator(form_id):
    """Return the generator callable for a form ID, or None."""
    info = get_generator(form_id)
    if info is None:
        return None
    mod_path, func_name = info
    if not mod_path.startswith("institutions."):
        mod_path = f"scripts.{mod_path}"
    return getattr(importlib.import_module(mod_path), func_name)
