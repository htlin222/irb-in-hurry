"""Form selector: maps (study type + phase) → required IRB forms.

Returns ordered list of (form_id, form_name_zh, generator_module, generator_func).
"""

# Form registry: form_id → (Chinese name, generator module path, function name)
FORM_REGISTRY = {
    # New case (新案審查)
    "SF001": ("新案審查送審資料表", "generators.new_case", "generate_sf001"),
    "SF002": ("研究計畫申請書", "generators.new_case", "generate_sf002"),
    "SF003": ("簡易審查範圍檢核表", "generators.consent", "generate_sf003"),
    "SF004": ("免予審查範圍檢核表", "generators.consent", "generate_sf004"),
    "SF005": ("免取得知情同意檢核表", "generators.consent", "generate_sf005"),
    "SF011": ("臨床試驗／研究許可證明", "generators.new_case", "generate_sf011"),
    "SF022": ("資料及安全性監測計畫", "generators.new_case", "generate_sf022"),
    "SF062": ("受試者同意書（臨床研究）", "generators.consent", "generate_sf062"),
    "SF063": ("受試者同意書（臨床試驗）", "generators.consent", "generate_sf063"),
    "SF075": ("受試者同意書（基因研究）", "generators.consent", "generate_sf075"),
    "SF090": ("受試者同意書（藥品試驗）", "generators.consent", "generate_sf090"),
    "SF091": ("受試者同意書（兒童）", "generators.consent", "generate_sf091"),
    "SF092": ("受試者同意書（醫療器材）", "generators.consent", "generate_sf092"),
    "SF094": ("顯著財務利益申報表", "generators.new_case", "generate_sf094"),
    # Amendment (修正案審查)
    "SF014": ("修正案審查送審資料表", "generators.amendment", "generate_sf014"),
    "SF015": ("修正案申請表", "generators.amendment", "generate_sf015"),
    "SF016": ("修正前後對照表", "generators.amendment", "generate_sf016"),
    # Re-review (複審案審查)
    "SF019": ("複審案申請表", "generators.re_review", "generate_sf019"),
    # Continuing review (期中審查)
    "SF030": ("期中審查送審資料表", "generators.continuing_review", "generate_sf030"),
    "SF031": ("期中報告書", "generators.continuing_review", "generate_sf031"),
    "SF032": ("計畫展延申請表", "generators.continuing_review", "generate_sf032"),
    # Closure (結案審查)
    "SF036": ("結案審查送審資料表", "generators.closure", "generate_sf036"),
    "SF037": ("結案報告摘要表", "generators.closure", "generate_sf037"),
    "SF038": ("結案報告書", "generators.closure", "generate_sf038"),
    "SF023": ("資料及安全性監測計畫報告書", "generators.closure", "generate_sf023"),
    # SAE (嚴重不良反應)
    "SF079": ("嚴重不良反應事件審查送審資料表", "generators.sae", "generate_sf079"),
    "SF044": ("嚴重不良反應事件通報表（本院）", "generators.sae", "generate_sf044"),
    "SF074": ("嚴重不良反應事件通報表（他院）", "generators.sae", "generate_sf074"),
    "SF080": ("試驗不遵從事件審查送審資料表", "generators.sae", "generate_sf080"),
    "SF024": ("試驗不遵從事件報告表", "generators.sae", "generate_sf024"),
    # IB update (主持人手冊)
    "SF082": ("更新主持人手冊審查送審資料表", "generators.ib_update", "generate_sf082"),
    "SF083": ("更新主持人手冊申請表", "generators.ib_update", "generate_sf083"),
    "SF084": ("多中心信函審查送審資料表", "generators.ib_update", "generate_sf084"),
    "SF085": ("多中心信函申請表", "generators.ib_update", "generate_sf085"),
    # Import (專案進口)
    "SF066": ("專案進口審查送審資料表", "generators.import_forms", "generate_sf066"),
    "SF067": ("專案進口申請表", "generators.import_forms", "generate_sf067"),
    "SF068": ("專案進口受試者同意書", "generators.import_forms", "generate_sf068"),
    "SF093": ("專案進口許可證明", "generators.import_forms", "generate_sf093"),
    # Suspension (計畫暫停/提前終止)
    "SF047": ("計畫暫停/提前終止審查送審資料表", "generators.suspension", "generate_sf047"),
    "SF048": ("計畫暫停/提前終止報告書", "generators.suspension", "generate_sf048"),
    # Appeal (申覆案)
    "SF077": ("申覆案審查送審資料表", "generators.appeal", "generate_sf077"),
    "SF054": ("申覆案申請表", "generators.appeal", "generate_sf054"),
    # Other
    "SF076": ("閱卷複印申請登記表", "generators.other", "generate_sf076"),
}

# Phase → form selection rules
PHASE_FORMS = {
    "new": {
        "base": ["SF001", "SF002", "SF094"],
        "conditions": [
            (lambda c: c["study"]["review_type"] == "expedited", ["SF003"]),
            (lambda c: c["study"]["review_type"] == "exempt", ["SF004"]),
            (lambda c: c["subjects"]["consent_waiver"], ["SF005"]),
            (lambda c: not c["subjects"]["consent_waiver"] and not c["study"]["drug_device"], ["SF062"]),
            (lambda c: not c["subjects"]["consent_waiver"] and c["study"]["drug_device"], ["SF063", "SF090"]),
            (lambda c: c["study"]["genetic"], ["SF075"]),
            (lambda c: c["subjects"].get("vulnerable_population"), ["SF091"]),
            (lambda c: c["study"]["review_type"] == "full_board", ["SF022"]),
        ],
    },
    "amendment": {
        "base": ["SF014", "SF015", "SF016", "SF094"],
        "conditions": [
            (lambda c: c["study"]["drug_device"], ["SF011"]),
        ],
    },
    "re_review": {
        "base": ["SF019"],
        "conditions": [],
    },
    "continuing": {
        "base": ["SF030", "SF031", "SF023"],
        "conditions": [
            (lambda c: c.get("continuing_review", {}).get("extension_requested"), ["SF032"]),
            (lambda c: c["study"]["drug_device"], ["SF011", "SF094"]),
        ],
    },
    "closure": {
        "base": ["SF036", "SF037", "SF038"],
        "conditions": [
            (lambda c: True, ["SF023"]),  # always include DSMP report for closure
        ],
    },
    "sae": {
        "base": ["SF079"],
        "conditions": [
            (lambda c: True, ["SF044"]),  # default: our site SAE report
        ],
    },
    "ib_update": {
        "base": ["SF082", "SF083"],
        "conditions": [
            (lambda c: c["study"]["multicenter"], ["SF084", "SF085"]),
        ],
    },
    "import": {
        "base": ["SF066", "SF067", "SF068"],
        "conditions": [
            (lambda c: True, ["SF093"]),
        ],
    },
    "suspension": {
        "base": ["SF047", "SF048"],
        "conditions": [],
    },
    "appeal": {
        "base": ["SF077", "SF054"],
        "conditions": [],
    },
}

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
    if form_id not in FORM_REGISTRY:
        return None
    _, mod_path, func_name = FORM_REGISTRY[form_id]
    return mod_path, func_name
