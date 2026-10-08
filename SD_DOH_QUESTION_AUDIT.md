# HEALIE SD-DOH question audit and adaptation log

## Status and intended use

This document records the design decisions applied to version `3.0.0-eu-gr` of the HEALIE Social and Digital Determinants of Health (SD-DOH) Assessment. It is an implementation and research audit trail, not evidence that the adapted instrument is psychometrically validated. Wording, translations, thresholds, skip logic and referral pathways require expert review and validation in the intended Greek and European populations before clinical or policy use.

- Participant-facing name: **Social and Digital Factors Affecting Health**
- Scientific name: **Social and Digital Determinants of Health (SD-DOH)**
- HEALIE component name: **HEALIE SD-DOH Assessment**
## Design principles

- Preserve the original 20-section SDoH core where it remains meaningful.
- Make optionality and decline choices explicit rather than interpreting missing data as a negative answer.
- Ask follow-up questions only when their parent response makes them relevant, and remove stale hidden answers.
- Keep adapted or newly authored modules identifiable as additions.
- Treat screening outputs as indicators, not diagnoses.
- Keep digital health literacy outside this component; it belongs in a separate HEALIE instrument.

## Question-by-question decisions

| Section | Topic | Decision and rationale |
|---:|---|---|
| 1 | Age | Added required age bands: 16–17, 18–21, 22–30, then decades through 71–80, 81+, and prefer not to answer. Age is required for age-specific physical-activity interpretation; decline produces `not_assessed`. |
| 1 | Gender | Added as optional: Woman, Man, Non-binary, Another gender, Prefer not to answer. “Another gender” opens required free text. |
| 1 | Ethnic group | Optional multi-select: White, Black or African, Asian, Hispanic/Latino, Arab, Other. “Other” opens required free text. Categories are project-defined and require local review. |
| 2 | Region and ancestry | Retained broad European region. Ancestry or ethnic origin is optional free text to preserve detail without forcing a category. |
| 3 | Household income | Retained existing EU/Greek adaptation and euro-denominated bands. |
| 4 | Education | Retained existing European education adaptation. |
| 5 | Work | Retained work status. Added conditional “last worked” for unemployed, homemaker, student, retired, or unable-to-work responses. |
| 6 | Housing | Housing tenure and housing-cost worry appear only for housed or housing-insecure participants. Monthly cost and difficulty paying appear only for rent or mortgage tenure. Currency is EUR. |
| 7 | Building | Added mobile home and limited the item to participants with housing. |
| 8 | Household | Household size constrained to 1–30 and bedrooms to 0–20; both are limited to participants with housing. Bounds are data-quality constraints, not clinical thresholds. |
| 9 | Residence | Retained residence duration. Postal code is optional, accepts 3–10 alphanumeric/space/hyphen characters, and the redundant multiple-residence item was removed. |
| 10 | Health coverage | Separated Other coverage from Not sure; Other requires specification. |
| 11 | Home internet | Retained the original yes/no item and made it conditional on having housing. Broader digital access is measured later. |
| 12 | Disability | Retained the six-item checklist, restored explicit completeness, and added age qualifiers to relevant ACS-style functional-difficulty wording. |
| 13 | Language | Retained local-language proficiency item. |
| 14 | Family | Modernized marital-status wording to include registered civil partnership and added Prefer not to say. Clarified single-parent wording in household terms. |
| 15 | Transport | Expanded EU-relevant modes; clarified that the mode covering most distance should be selected. Other opens free text. |
| 16 | Unmet needs | Restored the original five-row checklist: food, healthy food, healthcare/medicines, phone, and decline. Decline is exclusive. Any reported need reveals and requires all four original follow-ups (medical bills, delayed care, housing-cost worry, bill worry). |
| 17 | Social connection | Retained frequency item and added inclusive examples covering phone/online contact and community or club meetings. |
| 18 | Neighbourhood support | Retained as a distinct support statement and used British spelling. |
| 19 | PHQ-2 | Added an answer/decline gate. When answered, both rows are required. Sum 0–6; a score of at least 3 is flagged as a positive screen, not a diagnosis. |
| 19 | HITS | Added current-partner status and only displays HITS when Yes. Four 1–5 rows produce a 4–20 total; the implementation uses the English-language threshold of 11 and explicitly requires translated-version validation. |
| 19 | GAD-2 | Added an answer/decline gate. When answered, both rows are required. Sum 0–6; a score of at least 3 is flagged as a positive screen. |
| 19 | Cognition/MMSE | Retained self-reported cognition. MMSE total remains optional because it requires separate administration and governance. |
| 20 | Physical activity | If days are zero, minutes are hidden and weekly minutes equal zero. “150” is labelled “150 or more.” Ages 16–17 use 420 minutes/week (60 minutes/day); ages 18+ use 150 minutes/week. Missing/declined age yields `not_assessed`. This remains a simplified indicator because the item does not fully capture all WHO intensity guidance. |
| 21 | Religion | Removed. It was not part of the intended core questionnaire and had entered the earlier adaptation without a documented source or approved rationale. |
| 21 | Legal needs | Added as a separately documented, I-HELP-informed module: overall need, domains, optional Other specification, and access to support. It records potential unmet access without claiming a legal diagnosis. |
| 22 | Digital Access and Inclusion | Added six project-authored items covering suitable device access, reliable connectivity, affordability, accessibility/language inclusion, available support, and privacy/trust. These are a determinants screen, not a validated scale. |
| Deferred | eHEALS/digital literacy | Deliberately omitted from this assessment. Digital health literacy will be designed as a separate HEALIE component to avoid conflating structural digital determinants with individual skills. |

## Conditional and exclusivity rules

- `visible_if` supports equality and multi-select containment.
- Hidden answers are deleted in the frontend whenever a parent answer changes.
- A visible required question must be complete before section navigation and again on the server.
- Q16 decline is valid by itself and cannot be combined with checklist answers.
- Legal-domain “Prefer not to answer” is exclusive and cannot be combined with a substantive domain.
- Conditional free-text fields are required only while visible.

## Derived outputs

| Output | Rule |
|---|---|
| `phq2_score` / `depression_screen_positive` | Sum two PHQ-2 rows; flag at ≥3. |
| `hits_score` / `ipv_screen_positive` | Sum four HITS rows; flag at ≥11 for this English-language implementation. |
| `gad2_score` / `anxiety_screen_positive` | Sum two GAD-2 rows; flag at ≥3. |
| `weekly_minutes_activity` | Days × minutes; zero days produces zero. |
| `physical_activity_need` | Below 420 minutes for age 16–17 or below 150 for age 18+; `not_assessed` if age is unavailable. |
| `potential_unmet_legal_need` | True for partial/failed support or a stated knowledge, cost, or access barrier. |

## Source and rationale register

1. WHO Regional Office for Europe. *Addressing health determinants in a digital age: project report* (2024). https://www.who.int/europe/publications/i/item/WHO-EURO-2024-10917-50689-76724
2. WHO/Europe. *New WHO and London School of Economics study identifies key digital factors affecting health* (2 December 2024). https://www.who.int/europe/news/item/02-12-2024-new-who-and-london-school-of-economics-study-identifies-key-digital-factors-affecting-health
3. Kickbusch I, et al. *The digital determinants of health: a new era for global public health*. The Lancet (2026). https://doi.org/10.1016/S0140-6736(26)01292-4
4. National Center for Medical-Legal Partnership. *Screening Tool for MLP Legal Needs in Health Care Settings* (I-HELP-informed framework). https://www.medical-legalpartnership.org/mlp-resources/i-help-screening-tool
5. Kroenke K, Spitzer RL, Williams JBW. *The Patient Health Questionnaire-2: validity of a two-item depression screener* (2003). https://pubmed.ncbi.nlm.nih.gov/14583691/
6. Kroenke K, Spitzer RL, Williams JBW, Monahan PO, Löwe B. *Anxiety disorders in primary care: prevalence, impairment, comorbidity, and detection* (2007). https://pubmed.ncbi.nlm.nih.gov/17339617/
7. Sherin KM, Sinacore JM, Li XQ, Zitter RE, Shakil A. *HITS: a short domestic violence screening tool for use in a family practice setting* (1998). https://pubmed.ncbi.nlm.nih.gov/9669164/
8. WHO. *Physical activity* recommendations. https://www.who.int/europe/news-room/fact-sheets/item/physical-activity
9. Norman CD, Skinner HA. *eHEALS: The eHealth Literacy Scale* (2006). Retained as a reference for the deferred HEALIE digital-literacy component. https://pubmed.ncbi.nlm.nih.gov/17213046/

## Reporting language for a paper

The instrument was revised through an item-level audit that compared the existing EU/Greek implementation with the source questionnaire logic and contemporary literature. The original SDoH core was retained where possible, while branching, explicit optionality, decline responses and data-quality constraints were normalized across the schema, frontend and API. Religion items without a documented source were removed. Two clearly identified additions were introduced: an I-HELP-informed health-harming legal-needs module and a project-authored Digital Access and Inclusion module informed by WHO/Europe’s digital-determinants framework. Digital health literacy was intentionally deferred to a separate HEALIE component. These adaptations require cognitive interviewing, translation/back-translation, accessibility review and psychometric evaluation before substantive interpretation.