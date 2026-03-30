# IRB Reviewer Guide: Rules of Thumb & Checklists

## When to Use

When Claude acts as the simulated IRB reviewer (`make review`), follow this guide to evaluate generated forms like an experienced reviewer would. This is also the reference for users who serve as IRB committee members.

---

## The 8 Approval Criteria (45 CFR 46.111)

Every IRB review — full board, expedited, or continuing — must verify ALL eight:

| # | Criterion | Key Question |
|---|-----------|-------------|
| 1 | **Risk minimization** | Are procedures consistent with sound research design? |
| 2 | **Reasonable risk-benefit** | Do benefits justify the risks? |
| 3 | **Equitable selection** | Is subject selection fair and non-coercive? |
| 4 | **Informed consent sought** | Will consent be obtained appropriately? |
| 5 | **Consent documented** | Is written consent documented (or properly waived)? |
| 6 | **Safety monitoring** | Are there provisions to monitor data and safety? |
| 7 | **Privacy protected** | Are privacy and confidentiality adequately protected? |
| 8 | **Vulnerable safeguards** | Are additional protections in place for vulnerable groups? |

---

## Decision Framework

| Decision | Chinese | When to Use |
|----------|---------|-------------|
| Approve | 核准 | All 8 criteria met, no issues |
| Approve with modifications | 修改後核准 | Minor issues, clearly fixable |
| Defer | 擱置 | Cannot approve, but modifications might fix it |
| Disapprove | 否決 | Fundamental flaws, no modification can fix |

**Rule of thumb**: >90% of submissions get "修改後核准." Pure "核准" and "否決" are both rare.

---

## Red Flags Checklist

### Protocol Red Flags
- □ Sample size not justified or unreasonably large
- □ Procedures not necessary for research objectives
- □ Risk level inconsistent with review type claimed
- □ No data safety monitoring for >minimal risk study
- □ Investigator lacks relevant credentials/training
- □ Unclear primary endpoint or study objective

### Consent Red Flags
- □ Consent form contradicts protocol (different procedures, risks, or timelines)
- □ Technical jargon or undefined acronyms
- □ Reading level too high for target population
- □ Risks understated or benefits overstated
- □ Missing required elements (contact info, withdrawal rights, compensation)
- □ No re-consent plan when protocol changes
- □ "Anonymous" and "confidential" used interchangeably (they're different)

### Recruitment Red Flags
- □ Payment described as "benefit" rather than compensation
- □ Bonus contingent on study completion (coercive)
- □ PI has authority over potential subjects (teacher-student, employer)
- □ Recruitment materials not submitted for review

### Data/Privacy Red Flags
- □ No de-identification plan for identifiable data
- □ No encryption or access control described
- □ Data retention period not specified
- □ No breach notification plan
- □ Linking key stored without justification

---

## Risk Assessment Rules of Thumb

### How to Determine "Minimal Risk"

**The daily-life test**: Would a reasonable person encounter this risk in everyday life or routine medical exams?

| Risk Type | Minimal Risk Examples | Greater Than Minimal |
|-----------|----------------------|---------------------|
| Physical | Blood draw, vital signs, survey | New drug, biopsy, experimental device |
| Psychological | Questionnaire on daily habits | Questions about trauma, abuse, suicidal ideation |
| Social | Anonymous survey | Identifiable data about stigmatized behavior |
| Economic | No financial impact | Could affect employment or insurance |
| Legal | No legal exposure | Collecting data on illegal behavior |

### Risk-Benefit Weighing

1. **List ALL risks** — don't rely only on what investigator disclosed
2. **Assess probability AND magnitude** separately — high magnitude + low probability ≠ automatic rejection
3. **Count only research-related benefits** — therapy benefits don't count
4. **Knowledge importance counts** — even with no direct benefit, important knowledge can justify minimal risk

**Rule of thumb**: If the risk is that something "could" happen but would require multiple unlikely failures, it's probably minimal risk. If one routine failure exposes subjects to harm, it's greater than minimal.

---

## Review Type Quick Reference

### When Is Expedited Review Appropriate?

All of these must be true:
1. ■ Risk is minimal
2. ■ Procedures fall within expedited categories
3. ■ No identifiable data that could cause harm if disclosed
4. ■ No vulnerable populations (or adequate safeguards)

**Expedited categories that apply to KFSYSCC research**:
- ■ Retrospective chart review (existing records)
- ■ Non-invasive specimen collection (blood draw within limits)
- ■ Survey/interview with no sensitive topics
- ■ Minor changes to previously approved research

**Expedited reviewer CAN**: approve, require modifications, defer
**Expedited reviewer CANNOT**: disapprove (requires full board)

### When Is Full Board Required?

Any of these triggers full board:
- □ Greater than minimal risk
- □ Vulnerable populations without adequate safeguards
- □ Prisoner subjects (always full board)
- □ Novel interventions or experimental procedures
- □ Identifiable data about illegal behavior, stigmatized conditions

---

## Section-by-Section Review Questions

### 1. Scientific Design
- Is the hypothesis clearly stated?
- Is the design appropriate for the question?
- Is the sample size justified (not just "convenient")?
- Are endpoints clearly defined and measurable?
- For retrospective: is the data period sufficient?

### 2. Subject Selection
- Are inclusion/exclusion criteria clear and justified?
- Is the target population appropriate for this question?
- Are any vulnerable groups included? If so, why?
- Is recruitment non-coercive?

### 3. Informed Consent
- Does the form match the protocol exactly?
- Are ALL 8 basic elements present? (purpose, procedures, risks, benefits, alternatives, confidentiality, contacts, voluntary withdrawal)
- Is language at ≤8th grade reading level?
- Are risks described from the subject's perspective ("you may experience...")?
- Is the PI's phone AND email listed?
- Is the IRB office contact listed?
- For waiver: are all 4 waiver criteria met? (minimal risk, no adverse impact on rights, impractical to consent, post-hoc info provided)

### 4. Privacy & Confidentiality
- How is data collected? Stored? Transmitted?
- Is data de-identified or coded?
- Who has access to identifiable data?
- What happens to data when study ends?
- Is there a breach notification plan?

### 5. Risk Minimization
- Could a less risky procedure achieve the same goal?
- Are standard-of-care procedures used when possible?
- Are stopping rules defined for adverse events?
- Is there a qualified person to handle emergencies?

### 6. Data Safety Monitoring
- Is monitoring proportional to risk level?
- Who monitors? How often?
- What triggers early stopping?
- For retrospective minimal risk: "DSMP: PI monitors data quality" is sufficient

---

## Consent Waiver Checklist (Retrospective Studies)

For KFSYSCC retrospective chart reviews, verify ALL four criteria (45 CFR 46.116(f)(3)):

1. ■ Research involves no more than minimal risk
2. ■ Waiver will not adversely affect rights and welfare of subjects
3. ■ Research could not practicably be carried out without the waiver
4. ■ Whenever appropriate, subjects will be provided additional pertinent information after participation

**Rule of thumb for criterion 3**: If contacting hundreds of patients whose records span 5+ years is impractical (many may have died, moved, or lost contact), the waiver is justified. Document why.

---

## Common Mistakes in KFSYSCC Submissions

Based on institutional experience:

1. **Inconsistent IRB number** — different numbers on different forms
2. **Title mismatch** — English and Chinese titles describe different studies
3. **Missing co-PI disclosure** — co-PI not on SF094 financial disclosure
4. **Placeholder text** — "請填寫" left in submitted forms
5. **Wrong review type** — clinical trial marked as expedited
6. **Blank dates** — study period not specified
7. **Consent/protocol mismatch** — consent says 3 visits, protocol says 5
8. **No data period for retrospective** — "when were the charts from?"
9. **Sample size = 0** — forgot to specify
10. **Missing DSMP** — even minimal risk studies need basic safety monitoring

---

## Continuing Review Checklist

For annual/interim review, focus on CHANGES since last approval:

- □ Has the risk profile changed?
- □ Any new adverse events or safety signals?
- □ Is enrollment on track? Any significant deviations?
- □ Are consent documents still current?
- □ Any protocol violations or deviations?
- □ Does the study still meet all 8 approval criteria?
- □ Any new information that subjects should know?
- □ Any changes in investigator or research team?

**Rule of thumb**: Start from presumption that previously approved research still meets criteria. Focus on what's NEW or CHANGED.

---

## Taiwan-Specific Requirements

### Training Hours
- PI: 3 hours/year or 9 hours/3 years
- Co-PI/assistants: 2 hours/year or 6 hours/3 years
- Sources: CITI, Taiwan Academic Research Ethics Education Resource Center (臺灣學術倫理教育資源中心)

### Review Decisions (Taiwan Standard)
Same as international: 核准 / 修改後核准 / 擱置 / 否決

### NHI Impact on Research
- Drug availability constrained by NHI reimbursement — affects "standard of care" comparator
- NGS testing covered since May 2024 — impacts biomarker study feasibility
- CAR-T covered since Nov 2023 — enables real-world outcome studies

---

## References

- [45 CFR 46.111 — Criteria for IRB Approval](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46)
- [OHRP IRB Written Procedures Guidance](https://www.hhs.gov/ohrp/regulations-and-policy/guidance/institutional-issues/institutional-review-board-written-procedures/index.html)
- [FDA IRB FAQs](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/institutional-review-boards-frequently-asked-questions)
- [CITI IRB Protocol Review Training](https://about.citiprogram.org/course/irb-protocol-review/)
- [OHRP Expedited Review Categories](https://www.hhs.gov/ohrp/regulations-and-policy/guidance/categories-of-research-expedited-review-procedure-1998/index.html)
- [Taiwan Association of IRBs (TAIRB)](http://www.tairb.org.tw/)
