# Brainstorm: Clinical Research Ideas at KFSYSCC

## When to Use

When a user says they want to do research but doesn't have a specific topic, or wants to explore ideas. Use this reference to suggest study topics tailored to KFSYSCC's strengths.

## About KFSYSCC

- **Taiwan's only specialty cancer hospital** (est. 1990, 325 beds, 100% cancer)
- **19 dedicated cancer teams** covering all major cancer types
- **5-year survival: 74%** (vs. 57% Taiwan national average)
- **35 years of institutional data** (1990-present) in unified EHR
- **Harvard Business School case study** — value-based bundled payment breast cancer care model
- **Tumor tissue bank** + molecular tumor board + NGS (NHI-covered since May 2024)

## Taiwan Cancer Epidemiology (2022)

Top cancers by incidence:
1. Lung 2. Colorectal 3. Breast 4. Liver (HCC) 5. Oral 6. Prostate 7. Thyroid 8. Gastric 9. Skin 10. Endometrial

**Taiwan-unique patterns** (vs. Western countries):
- **Oral cancer**: 85% attributable to areca nut (betel quid), NOT tobacco — different molecular pathways
- **NPC**: 6.17/100,000 (vs. <1 in West) — EBV-driven, declining but still high
- **HCC**: HBV/HCV endemic — surveillance and early detection research
- **NSCLC in never-smokers**: Significant proportion, EGFR mutations more common in Asian populations
- **Breast cancer**: Triple-negative subtype has different genetic profile in Asian women

## Study Design Templates

### Template A: Retrospective Cohort (Most Common at KFSYSCC)

```
Topic: [Treatment/Exposure] and [Outcome] in [Cancer Type] patients
Design: Single-center retrospective cohort, KFSYSCC [Year]-[Year]
Population: [Cancer type], [Stage], [Treatment]
Primary endpoint: [Survival metric / clinical outcome]
Statistical method: Propensity score matching, Cox regression
Expected N: [based on KFSYSCC volume]
Review type: Expedited (minimal risk, chart review)
Consent: Waiver (retrospective, de-identified)
```

### Template B: Biomarker/Precision Medicine

```
Topic: [Biomarker/Mutation] as predictor of [Response/Outcome] in [Cancer]
Design: Retrospective biomarker-outcome correlation
Data source: KFSYSCC tumor tissue bank + NGS database
Population: [Cancer type] with available molecular profiling
Primary endpoint: [Biomarker] association with [Outcome]
Secondary: Treatment selection patterns based on molecular results
```

### Template C: Treatment Comparison (Real-World Evidence)

```
Topic: [Treatment A] vs [Treatment B] in [Cancer Type]: real-world outcomes
Design: Retrospective comparative effectiveness, PSM
Population: Consecutive patients receiving either treatment
Primary endpoint: Overall survival / progression-free survival
Key covariates: Stage, performance status, comorbidities
Advantage: NHI ensures equitable access (reduces insurance confounding)
```

### Template D: Quality/Value-Based Care

```
Topic: Impact of [MDT intervention / care process] on [Outcome]
Design: Before-after or comparative cohort
Data source: Institutional quality metrics + outcomes data
Advantage: KFSYSCC's bundled payment model is uniquely measurable
```

## High-Value Research Topics by Cancer Type

### Breast Cancer (KFSYSCC flagship program)
- Optimal chemotherapy sequencing (neoadjuvant vs adjuvant) by molecular subtype
- G-CSF timing in chemotherapy-induced neutropenia (proven topic — see irb-close)
- TNBC recurrence prediction in Asian women (different from Western signatures)
- Long-term cardiac toxicity of anthracycline regimens
- Value of MDT on stage-specific survival (unique bundled payment data)
- Survivorship outcomes: return to work, quality of life, psychosocial

### Lung Cancer
- EGFR-TKI skin toxicity as response predictor (proven topic — see mock proposal)
- ICI-induced thyroid dysfunction and clinical outcomes (proven topic — see mock fixture)
- Sequential therapy patterns: EGFR-TKI → ICI → chemotherapy
- Never-smoker NSCLC: molecular landscape and treatment response
- Real-world osimertinib outcomes in T790M+ patients

### Head & Neck / Oral Cancer (Taiwan-unique)
- Areca nut exposure grading and oral cancer prognosis
- p16/HPV status in oropharyngeal carcinoma (rising incidence in Taiwan)
- IMRT outcomes in NPC: long-term toxicity and quality of life
- Second primary cancer risk after NPC treatment
- De-escalation strategies for low-risk NPC

### Liver Cancer (HCC)
- HBV/HCV surveillance adherence and stage at diagnosis
- Immunotherapy (atezolizumab + bevacizumab) real-world outcomes
- TACE vs ablation: comparative effectiveness by tumor size
- Biomarker-guided treatment selection (AFP, PIVKA-II, ctDNA)

### Colorectal Cancer
- Sidedness (left vs right) and treatment response patterns
- MSI-H/dMMR prevalence and immunotherapy outcomes in Taiwanese patients
- Liquid biopsy (ctDNA) for minimal residual disease monitoring
- Neoadjuvant chemoradiation vs total neoadjuvant therapy in rectal cancer

### Hematologic Malignancies
- CAR-T therapy outcomes (NHI-covered from Nov 2023)
- DLBCL: Waldeyer ring vs nodal — outcomes and molecular differences
- R-CHOP real-world outcomes in elderly patients

### Cross-Cutting Topics
- NGS testing patterns and actionable mutation rates since NHI coverage (May 2024)
- MDT timing: does early MDT discussion improve outcomes?
- Immunotherapy irAE management patterns and impact on response
- Financial toxicity under NHI: out-of-pocket burden for cancer patients
- Polypharmacy in elderly cancer patients: drug interactions and outcomes
- Palliative care integration timing and survival impact

## Standard Limitations (include in every KFSYSCC study)

Copy-paste into your discussion section:

1. **Single-center design**: Results from KFSYSCC may not generalize to other institutions or healthcare systems
2. **Retrospective design**: Inherent selection bias and unmeasured confounders
3. **Referral bias**: KFSYSCC patients may represent a selected population (specialty cancer center)
4. **Ethnic homogeneity**: Predominantly Taiwanese Chinese; limited generalizability to other ethnicities
5. **Temporal changes**: Treatment protocols and staging criteria evolved over the study period
6. **NHI constraints**: Drug availability and treatment patterns influenced by NHI reimbursement policies

## Standard Strengths

1. **Standardized care**: MDT-based protocols minimize treatment variability
2. **Complete data**: Single EHR system with comprehensive documentation
3. **Long follow-up**: 35-year institutional data enables mature outcome analysis
4. **NHI system**: Universal coverage reduces insurance-related confounding
5. **High volume**: Dedicated cancer center with sufficient case numbers for subgroup analysis

## How to Use with Distill

After brainstorming, the user can say something casual like:

> "好，那我想做 EGFR-TKI 皮膚毒性和治療反應的回顧性研究"

Claude should then:
1. Save to `raw/`
2. Distill to `config.toml` (+ `cv.toml`, `中文計畫摘要.md`) using [distill.md](distill.md)
3. Generate forms with `make all`
4. Run reviewer with `make review`
