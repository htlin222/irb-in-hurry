"""IRB review criteria checklist.

Based on 45 CFR 46.111 (federal approval criteria) and common
institutional review patterns from Taiwan IRB standards (KFSYSCC as reference).
"""

REVIEW_CRITERIA = {
    "completeness": {
        "name": "文件完整性",
        "name_en": "Document Completeness",
        "regulatory_basis": "Institutional SOP",
        "items": [
            ("forms_complete", "All required forms for this phase are generated"),
            ("irb_no_consistent", "IRB number consistent across all forms"),
            ("title_consistent", "Study title (zh+en) consistent across all forms"),
            ("pi_consistent", "PI name consistent across all forms"),
            ("dates_present", "Study dates present and not blank"),
            ("copi_listed", "Co-PI listed in relevant forms"),
            ("footer_present", "Version/form number footer present on each form"),
        ],
    },
    "consent": {
        "name": "知情同意",
        "name_en": "Informed Consent",
        "regulatory_basis": "45 CFR 46.116, 46.117",
        "items": [
            ("consent_waiver_justified", "Consent waiver justified for retrospective/exempt studies"),
            ("consent_elements", "Consent form includes all required elements (if applicable)"),
            ("contact_info", "Contact info (PI + IRB office) present in consent form"),
            ("signature_blocks", "Signature blocks present and complete"),
        ],
    },
    "risk_benefit": {
        "name": "風險效益評估",
        "name_en": "Risk-Benefit Assessment",
        "regulatory_basis": "45 CFR 46.111(a)(1-2)",
        "items": [
            ("risk_level_match", "Risk level matches review type (minimal risk → expedited)"),
            ("risk_minimization", "Risk minimization strategies described"),
            ("benefits_stated", "Anticipated benefits clearly stated"),
        ],
    },
    "privacy": {
        "name": "隱私與保密",
        "name_en": "Privacy & Confidentiality",
        "regulatory_basis": "45 CFR 46.111(a)(7)",
        "items": [
            ("deidentification", "De-identification or anonymization method described"),
            ("data_security", "Data storage and security procedures addressed"),
            ("retention_period", "Data retention period specified"),
            ("access_control", "Authorized personnel for data access documented"),
        ],
    },
    "subject_selection": {
        "name": "受試者選取",
        "name_en": "Subject Selection",
        "regulatory_basis": "45 CFR 46.111(a)(3)",
        "items": [
            ("sample_size", "Sample size stated and reasonable"),
            ("vulnerable_flag", "Vulnerable population flag matches study content"),
            ("selection_equitable", "Subject selection is equitable and non-coercive"),
        ],
    },
    "study_design": {
        "name": "研究設計",
        "name_en": "Study Design",
        "regulatory_basis": "45 CFR 46.111(a)(1)",
        "items": [
            ("type_forms_match", "Study type matches selected form set"),
            ("data_period_scope", "Data collection period covers research scope"),
            ("design_consistent", "Study design description consistent across forms"),
        ],
    },
    "administrative": {
        "name": "行政合規",
        "name_en": "Administrative Compliance",
        "regulatory_basis": "Institutional SOP",
        "items": [
            ("financial_disclosure", "Financial disclosure form (SF094) included"),
            ("all_signatures", "All required signature blocks present"),
            ("current_versions", "Form versions are current (2025.03.03 where applicable)"),
            ("submission_noted", "Submission instructions noted (institution submission address)"),
        ],
    },
}

# Common placeholder strings that indicate incomplete forms
# Note: "＿＿" is excluded — it's used for intentional signature/date blanks
PLACEHOLDER_PATTERNS = [
    "請填寫",
    "（請說明）",
    "placeholder",
    "TODO",
    "TBD",
]

# Review decision types (Taiwan standard)
DECISIONS = {
    "approved": "核准 (Approved)",
    "approved_with_revisions": "修改後核准 (Approved Contingent Upon Revisions)",
    "tabled": "擱置 (Tabled)",
    "disapproved": "否決 (Disapproved)",
}

# Finding severity levels
SEVERITY = {
    "required": "必須修正",
    "suggestion": "建議修改",
    "note": "備註",
}
