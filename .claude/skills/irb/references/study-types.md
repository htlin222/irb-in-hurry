---
name: study-types
description: Decision tree for classifying study types and routing to the correct IRB review pathway and forms.
---

# Study Type Classification & Routing

## Decision Tree

```
Is this research involving human subjects?
├── No → No IRB needed
└── Yes
    ├── Retrospective data only? (chart review, database analysis)
    │   └── Yes → RETROSPECTIVE
    │       review_type: expedited
    │       consent_waiver: true
    │       Forms: SF001, SF002, SF094, SF003, SF005
    │
    ├── Prospective but no intervention? (observational, survey, interview)
    │   └── Yes → PROSPECTIVE
    │       review_type: expedited (minimal risk) or full_board (more than minimal)
    │       Forms: SF001, SF002, SF094, SF003 or SF022, SF062
    │
    ├── Interventional drug or device trial?
    │   └── Yes → CLINICAL_TRIAL
    │       review_type: full_board
    │       drug_device: true
    │       Forms: SF001, SF002, SF094, SF022, SF063, SF090
    │       If device: + SF092
    │
    ├── Involves genetic data or specimens?
    │   └── Yes → GENETIC (or add genetic flag to other types)
    │       review_type: full_board
    │       genetic: true
    │       Forms: base forms + SF075
    │
    └── Multi-center study?
        └── Add multicenter: true
            Additional: SF084, SF085 (for IB updates)
```

## Config Mapping

### Retrospective Chart Review

```yaml
study:
  type: retrospective
  design: cohort          # or case_control, cross_sectional
  review_type: expedited
  drug_device: false
  genetic: false
subjects:
  consent_waiver: true
```

Auto-inferred by `form_selector._apply_study_type_defaults()`:
- `consent_waiver` is set to `true`
- `review_type` defaults to `expedited` if not specified

### Prospective Observational

```yaml
study:
  type: prospective
  design: cohort          # or cross_sectional
  review_type: expedited  # or full_board if more than minimal risk
  drug_device: false
subjects:
  consent_waiver: false   # typically requires consent
```

### Clinical Trial

```yaml
study:
  type: clinical_trial
  design: rct
  review_type: full_board
  drug_device: true
subjects:
  consent_waiver: false
  vulnerable_population: false  # set true if includes minors/prisoners/etc.
```

### Genetic Research

```yaml
study:
  type: genetic
  review_type: full_board
  genetic: true
subjects:
  consent_waiver: false
```

## Review Type Criteria

### Exempt (`exempt`)
- Educational research
- Survey/interview with de-identified data
- Existing public data analysis
- Forms: SF004 (exemption checklist)

### Expedited (`expedited`)
- Minimal risk research
- Retrospective chart review
- Prospective observational with minimal risk
- Forms: SF003 (expedited checklist)

### Full Board (`full_board`)
- More than minimal risk
- All clinical trials
- Genetic research
- Vulnerable populations
- Forms: SF022 (DSMP required)

## Vulnerable Population Flags

When `vulnerable_population: true`:
- Additional consent form SF091 (children's assent)
- Full board review required regardless of study type
- Extra justification needed in SF002
