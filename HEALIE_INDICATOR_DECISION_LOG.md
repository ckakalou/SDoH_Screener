# HEALIE indicator decision log

## Purpose

This document records the scientific and conceptual decisions used to derive
HEALIE indicators from the Social and Digital Determinants of Health (SD-DOH)
assessment. It is intentionally separate from `SD_DOH_QUESTION_AUDIT.md`, which
documents questionnaire wording, branching, validation, schema, and other
implementation decisions.

The indicator log records:

- the construct represented by each indicator;
- the questionnaire inputs used to derive it;
- the supporting literature and limitations of that evidence;
- the calculation, categories, and handling of missing or declined answers;
- whether the indicator should be retained by HEALIE;
- inappropriate interpretations that the implementation must avoid; and
- potential relevance to the full HEALIE personalisation profile; and
- decisions deferred to the later HEALIE knowledge-representation and
  personalisation phase.

This is a living research and design record. The indicators are intended to
support personalisation and must not be described as diagnoses. Cut-offs from
validated instruments remain screening thresholds and must be used in
accordance with the conditions under which those instruments were validated.

## Current scope and deferred work

### Current operational scope

The assessment will validate item-level answers and calculate approved derived
indicators. HEALIE will retain or receive the derived indicators and essential
provenance metadata rather than the participant's complete item-level response.
The intended provenance metadata includes a random submission identifier,
questionnaire version, scoring version, assessment timestamp, and explicit
assessment status where relevant.

The application must distinguish `not_assessed`, `declined`, `not_applicable`,
and a substantive negative result. A missing value must never be interpreted as
absence of need.

### Deferred research and validation mode

Collection of pseudonymised item-level responses for psychometric evaluation,
instrument validation, recalculation, or research reproducibility is deferred
until real-patient research is planned and the necessary ethics, consent, data
protection, hosting, and institutional-governance requirements have been
approved.

### HEALIE health-literacy and personalisation architecture

HEALIE is based on Sørensen's integrated model of health literacy. The four
dimensions **Access, Understand, Appraise, and Apply** remain the central
conceptual scaffold; social, personal, emotional, and digital factors are not a
competing set of dimensions.

The knowledge-representation pathway is:

1. a measured or derived **factor/indicator**;
2. a provenance-bearing, weighted relationship from that factor to one or more
   **health-literacy dimensions**, where supported;
3. one or more **adaptations** intended to reduce the associated demand or
   support the participant; and
4. the concrete **content, interface, modality, tone, structure, or resource
   feature** that implements the adaptation.

The ontology therefore preserves the distinct edge families
`Factor -> HealthLiteracyDimension`, `Factor -> Adaptation`, and
`Adaptation -> TextOrInterfaceFeature`. A direct adaptation edge does not create
a fifth health-literacy dimension. It records how HEALIE responds to a factor
and should, where applicable, document which Sørensen dimension or dimensions
the adaptation is intended to support.

For example, digital and interface accessibility most directly affect
**Access** because they influence whether a person can seek, reach, and obtain
health information. Legibility, navigation, or interaction design may also
affect **Understand** or **Apply**, so the mapping must reflect the mechanism
rather than force every interface feature into Access alone. Emotional context
is expected to influence **Appraise** and especially **Apply** most strongly,
while anxiety or cognitive load may also affect Understand in some settings.

The published HEALIE work established the four-dimension model and described
ranking relevant factors and incorporating their importance as weights. Its
implemented scope initially concentrated on Understand and Appraise; extending
the operational model to Access and Apply is therefore an explicit development
of that work, not a replacement of it. Numerical weights reported or encoded in
the earlier publications and knowledge graph will be retained with their source
and version as prior weights. They will not be silently overwritten by the
present indicator review. New or revised SDoH/DDoH relationships will be marked
as proposed until their rationale, scale, direction, and provenance have been
reviewed, and all weights remain candidates for later expert and patient
validation.

Some adaptations may concern clinical or contextual relevance rather than a
health-literacy capability—for example, selecting an age-appropriate clinical
recommendation. Such a pathway must be labelled separately and must not be
misrepresented as an effect on a health-literacy dimension.

### Deferred HEALIE personalisation decisions

The following decisions are explicitly deferred until development of the main
HEALIE personalisation system:

- the influence weight of each indicator on the four health-literacy dimensions
  (Access, Understand, Appraise, and Apply), where such a relationship is
  justified;
- the rules by which relevant indicators are combined to estimate a
  participant's health-literacy needs or level;
- the precise dimension mappings for each factor, including whether a
  relationship is direct, indirect, moderating, or unsupported;
- the mapping from an indicator to adaptations of content, interface, modality,
  timing, tone, structure, explanation, or recommended resources; and
- interaction effects among indicators.

The present phase determines what an indicator means and how it is calculated.
It also records plausible relationships to the four health-literacy dimensions
and possible adaptations, but it does not yet assign new causal effects,
personalisation rules, or weights. No overall SDoH, vulnerability, or
health-literacy risk score will be created without a separate evidence-based and
validated model.

### Interpretation categories used for each indicator

Each indicator will be considered across the following pathways:

1. **Access:** ability to seek, find, reach, and obtain suitable health
   information or services, including relevant digital and interface barriers.
2. **Understand:** ability to comprehend the information that is accessed.
3. **Appraise:** ability to interpret, evaluate, and judge information in its
   personal and emotional context.
4. **Apply:** ability to decide and act on information in real circumstances,
   including financial, employment, transport, housing, caregiving, safety, and
   social constraints.
5. **Adaptation pathway:** the communication, content, interface, modality,
   emotional-support, navigation, or resource response through which HEALIE may
   support those dimensions.
6. **Contextual relevance:** a non-health-literacy rule, such as selecting an
   age-appropriate recommendation, recorded separately from dimension effects.

An indicator may relate to several dimensions and adaptations without being
used to calculate a single health-literacy level. Relationships must not be
inferred merely because an adaptation seems intuitively useful.

## Decision status vocabulary

| Status | Meaning |
|---|---|
| Proposed | Under discussion; not approved for implementation. |
| Approved | Scientific and conceptual definition agreed. |
| Implemented | Approved definition is represented in code and tests. |
| Deferred | Intentionally postponed to a later research or HEALIE phase. |
| Rejected | Considered but should not be implemented. |

## Indicator 1: age-related context

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source item

- **Source:** participant-reported age band.
- **Classification:** contextual factor, not a health-literacy deficit and not
  an adverse SDoH indicator by itself.
- **Potential retained outputs:** `age_band` and, if required by an age-specific
  rule, a derived `life_stage` or `recommendation_group`.

### Evidence review

The literature supports a population-level association between older age and
limited health literacy, but the size and meaning of the association depend
strongly on the construct and instrument used.

Kobayashi et al.'s systematic review and meta-analysis included 70 analyses in
60 studies of adults aged 50 years and older. Older age was strongly associated
with limited health literacy when instruments assessed reading comprehension,
reasoning, and numeracy (random-effects odds ratio 4.20, 95% confidence interval
3.13-5.64). The association was much weaker when instruments primarily assessed
medical vocabulary (odds ratio 1.19, 95% confidence interval 1.03-1.37). The
authors concluded that performance on tasks using fluid cognitive abilities is
more sensitive to ageing than vocabulary-based ability.

The European Health Literacy Survey found a higher prevalence of limited health
literacy among older people, alongside financial deprivation, lower social
status, and lower educational attainment. The result therefore reflects a wider
social gradient and does not establish age as an isolated individual-level
cause.

Longitudinal evidence also indicates heterogeneity. In the English Longitudinal
Study of Ageing, health-literacy decline increased with age, while cognitive
function and subtle cognitive decline explained an important part of the
relationship. In the ACTIVE cohort of adults aged 65 years and older, age,
education, cognition, vision, and other sociodemographic factors were associated
with health literacy. Scores were relatively stable during much of the ten-year
follow-up, although older participants began with lower scores and subsequently
declined more quickly.

These findings indicate that age can be associated with difficulties in some
functional health-literacy tasks, but it does not uniformly reduce all forms of
health literacy. Crystallised knowledge, accumulated health-system experience,
and medical vocabulary may remain stable, while reasoning, processing,
numeracy, sensory access, or working memory may be more vulnerable. Education,
cognition, vision, hearing, language, socioeconomic circumstances, and digital
experience should be represented directly where those data are available.

### Approved interpretation

Age is a contextual HEALIE factor that may inform age-specific rules and may
contribute cautiously to later personalisation models. Its relevance is not
limited to health literacy: age may affect the applicability of clinical or
public-health recommendations, examples, accessibility options, interface
preferences, service pathways, and life-stage context. It must not independently
determine that a person has low health literacy or has a particular accessibility
need.

There is no approved age threshold at which HEALIE will classify a participant
as having limited health literacy. Conventional boundaries such as 65 years may
define study populations or life stages, but they are not health-literacy
cut-offs.

### Approved calculation and representation

For the current phase:

```json
{
  "age_context": {
    "assessment_status": "assessed",
    "age_band": "71_80",
    "life_stage": "older_adult"
  }
}
```

If the participant declines to provide age:

```json
{
  "age_context": {
    "assessment_status": "declined"
  }
}
```

Age may also select an evidence-based recommendation group for another
indicator, such as physical activity. If age is unavailable, that age-dependent
indicator must return `not_assessed` rather than select an arbitrary adult
threshold.

### Prohibited inferences

The implementation must not derive any of the following from age alone:

- `low_health_literacy: true`;
- cognitive impairment;
- inability to use digital technology;
- inability to understand detailed information;
- a need for simplified content; or
- social vulnerability.

Direct measures of education, language proficiency, cognition, vision, hearing,
digital access, or health literacy should take precedence over age whenever the
relevant construct is available.

### Deferred HEALIE decisions

- Whether `age_band` must be retained after all age-dependent indicators have
  been calculated.
- The weight, if any, of age on Access, Understand, Appraise, or Apply.
- Whether age modifies another factor rather than having a direct link to a
  health-literacy dimension.
- The exact content, recommendation, resource, accessibility, or interface
  adaptations associated with age.
- Which adaptations require direct evidence from vision, hearing, cognition,
  disability, digital access, or participant preference rather than age.

### References

1. Kobayashi LC, Wardle J, Wolf MS, von Wagner C. Aging and Functional
   Health Literacy: A Systematic Review and Meta-Analysis. *J Gerontol B
   Psychol Sci Soc Sci.* 2016;71(3):445-457.
   https://doi.org/10.1093/geronb/gbu161
2. Sørensen K, Pelikan JM, Röthlin F, et al. Health literacy in Europe:
   comparative results of the European Health Literacy Survey (HLS-EU).
   *Eur J Public Health.* 2015;25(6):1053-1058.
   https://doi.org/10.1093/eurpub/ckv043
3. Kobayashi LC, Wardle J, Wolf MS, von Wagner C. Cognitive Function and
   Health Literacy Decline in a Cohort of Aging English Adults. *J Gen Intern
   Med.* 2015;30(7):958-964.
   https://doi.org/10.1007/s11606-015-3206-9
4. Yu L, Wilson RS, Han SD, et al. Health Literacy, Sociodemographic Factors,
   and Cognitive Training in the ACTIVE Study of Older Adults. *Int J Aging
   Hum Dev.* 2020;90(3):292-310.
   https://doi.org/10.1177/0091415019843446

## Indicator 2: household income and economic vulnerability

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source items

- **Primary source:** annual household-income band from
  `q3_household_income`.
- **Related direct measures:** housing-payment difficulty, concern about housing
  costs, unmet material or health-care needs, and concern about normal monthly
  bills.
- **Classification:** household income is a contextual variable. Experienced
  affordability problems and unmet needs are direct indicators.

### Evidence review

The literature generally reports an association between lower income or
financial deprivation and limited health literacy. A systematic scoping review
found this association across several health-literacy domains, although the
evidence was heterogeneous and predominantly observational. It does not justify
inferring an individual's health-literacy level directly from income.

In the European Health Literacy Survey, financial deprivation was among the
social determinants most strongly related to health literacy. In the combined
European sample, 63.4% of people who reported difficulty paying bills most of
the time had limited health literacy; the corresponding proportion reported for
Greece was 60.7%. Recent cross-sectional evidence from a convenience sample in
Greece and Cyprus also reported higher general health literacy among people with
higher incomes. The latter sample was relatively young and digitally recruited,
so it should not be interpreted as nationally representative.

The official EU at-risk-of-poverty indicator cannot be calculated from a simple
income band. Eurostat defines it as equivalised disposable household income
after social transfers below 60% of the national median. The threshold is
country-specific and changes by income reference year. The equivalence
calculation also requires household composition rather than only the total
number of residents.

For the Greek 2025 EU-SILC results, using income from 2024, ELSTAT reported a
threshold of EUR 7,020 for a single-person household and EUR 14,742 for a
household with two adults and two dependent children younger than 14. These
figures illustrate why a fixed project threshold would become outdated and why
the same nominal household income cannot be interpreted without household
composition.

The current assessment asks for a broad annual household-income band and total
household size. It does not clearly request net disposable income after social
transfers or distinguish adults from dependent children. Some bands cross the
official poverty threshold, and household size is not collected for every
housing situation. It therefore cannot support an official or approximate
at-risk-of-poverty classification with acceptable validity.

### Approved interpretation

Household income is associated with health literacy at population level, but
the current categorical income item is insufficient to classify individual
poverty, low income, financial vulnerability, or health-literacy level.

Directly reported difficulty paying housing costs, concern about bills, and
inability to obtain necessities are more proximal and actionable indicators for
HEALIE than an arbitrary classification based on the income band. Their HEALIE
relevance extends beyond any association with health literacy: they may affect
whether recommendations are affordable or feasible and whether lower-cost
alternatives, benefit information, navigation support, or social-service
resources should be offered.

### Approved calculation and representation

The operational derived payload will not retain the participant's original
household-income band at this stage. It may retain assessment status if needed
for provenance, but will not convert the band into a substantive classification.

Direct economic difficulties will be represented separately in their relevant
domains. A possible structure, to be finalised when those domains are reviewed,
is:

```json
{
  "economic_context": {
    "income_assessment_status": "assessed"
  },
  "housing_affordability": {
    "payment_difficulty": true,
    "cost_concern": "moderate"
  },
  "material_needs": {
    "food_unmet": false,
    "healthy_food_unmet": true,
    "healthcare_unmet": false,
    "phone_unmet": false
  },
  "general_bill_concern": {
    "assessment_status": "assessed",
    "level": "very_worried"
  }
}
```

The absence of the conditional general-bills question means `not_assessed`, not
absence of financial strain.

### Prohibited inferences

The current household-income answer must not produce:

- `at_risk_of_poverty: true`;
- `low_income: true`;
- a diagnosis of financial vulnerability;
- `low_health_literacy: true`; or
- a numeric economic-vulnerability or health-literacy score.

An overall financial-strain score must not be produced by simply adding the
existing affordability, worry, and unmet-need responses. They do not currently
constitute a validated unidimensional scale and are not administered under the
same eligibility conditions.

### Deferred HEALIE decisions

- Whether a future, necessary personalisation use justifies retaining a coarser
  income context.
- Whether the income item should later be redesigned to collect the components
  required for equivalised disposable income.
- The relationship and weights between direct financial-strain indicators and
  Access, Understand, Appraise, or Apply.
- Whether a validated multidimensional financial-strain measure should replace
  or supplement the current questions.
- How economic constraints should modify the feasibility and affordability of
  recommended actions, and which support or navigation resources should be
  offered.

### References

1. Gero K, Backhaus-Hoven I, Höhmann A, Dragano N, Hoven H. Low income and
   health literacy: a systematic scoping review. *Arch Public Health.*
   2025;83:291. https://doi.org/10.1186/s13690-025-01781-3
2. Sørensen K, Pelikan JM, Röthlin F, et al. Health literacy in Europe:
   comparative results of the European Health Literacy Survey (HLS-EU).
   *Eur J Public Health.* 2015;25(6):1053-1058.
   https://doi.org/10.1093/eurpub/ckv043
3. Eurostat. Glossary: At-risk-of-poverty rate.
   https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:At-risk-of-poverty_rate
4. Hellenic Statistical Authority. Risk of poverty or social exclusion, 2025
   survey results, income reference year 2024.
   https://www.statistics.gr/documents/20181/30dc21b1-d0b6-feb9-beca-62e75e6b0d86
5. Associations of Health and Digital Health Literacy with Health-Related
   Quality of Life: A Cross-Sectional Study in Greece and Cyprus. *Journal of
   Health Literacy.* 2026;11(1):64-79.

## Indicator 3: educational attainment context

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source item

- **Source:** highest completed level of education from `q4_education`.
- **Classification:** contextual personalisation factor, not a direct measure of
  health literacy.
- **Retained outputs:** a broad attainment group and the detailed attainment
  category reported through the questionnaire.

### Evidence review

Educational attainment is consistently associated with health literacy at
population level. The European Health Literacy Survey reported a clear social
gradient. Across the eight participating countries, 68.0% of participants in
the lowest education categories had limited health literacy; the corresponding
proportion reported for Greece was 77.3%. At the next educational level,
limited health literacy remained common: 57.2% overall and 55.8% in Greece.
Education remained associated with health literacy in multivariable analysis,
although financial deprivation and perceived social status were stronger
predictors.

The later HLS19 programme continued to demonstrate social gradients across
general and specific health-literacy domains. Nevertheless, meaningful
within-group variation remains. Research in higher-education populations also
identifies participants with limited health literacy, demonstrating that a
university degree cannot establish adequate health literacy.

Formal education may contribute reading, numeracy, reasoning, and
information-evaluation skills, and is also related to occupational and economic
opportunities. Health literacy additionally depends on health-system
experience, language, cognition, digital skills, illness complexity, emotional
state, and the demands imposed by the information and service environment.
Experiential health knowledge may also be substantial among people with less
formal education.

### Approved interpretation

Educational attainment provides relevant context for HEALIE and may later
inform personalisation through communication and content pathways as well as
through a possible relationship with health literacy. It may be relevant to the
assumed familiarity of examples, numeracy demands, explanation depth, structure,
and learning support. It does not directly measure an individual's ability to
access, understand, appraise, or apply health information. No education category
establishes adequate or limited health literacy, and there is no approved
educational cutoff for such a classification.

Both a broad attainment group and the detailed questionnaire category will be
retained. Keeping the detailed category preserves the distinction between
undergraduate, master's, and doctoral education without prematurely assuming
that these levels require different adaptations.

### Approved calculation and representation

```json
{
  "education_context": {
    "assessment_status": "assessed",
    "attainment_group": "tertiary",
    "attainment_detail": "masters"
  }
}
```

The agreed mapping is:

| Questionnaire value | `attainment_group` | `attainment_detail` |
|---|---|---|
| `no_formal` | `below_secondary` | `no_formal` |
| `primary` | `below_secondary` | `primary` |
| `lower_secondary` | `below_secondary` | `lower_secondary` |
| `upper_secondary` | `secondary` | `upper_secondary` |
| `vocational` | `vocational` | `vocational` |
| `undergraduate` | `tertiary` | `undergraduate` |
| `masters` | `tertiary` | `masters` |
| `doctorate` | `tertiary` | `doctorate` |
| `prefer_not_to_say` | omitted | omitted; status is `declined` |

Vocational education remains its own broad group because vocational programmes
can represent different levels across Greek and other European education
systems. It must not be forced into secondary or tertiary without more specific
programme information.

### Prohibited inferences

Educational attainment alone must not produce:

- `low_health_literacy: true`;
- `adequate_health_literacy: true`;
- `low_education: true`;
- a cognitive, reading, or numeracy impairment; or
- an automatic requirement for simplified or advanced content.

Direct health-literacy evidence should take precedence when available.

### Deferred HEALIE decisions

- The relationship and weights between education and Access, Understand,
  Appraise, or Apply.
- Whether education modifies other factors rather than acting directly on a
  health-literacy dimension.
- The content, interface, explanation, or modality adaptations associated with
  education.
- Whether undergraduate, master's, and doctoral attainment should have
  different effects in the final model.
- Whether education should affect explanation structure or learning support
  directly, independently of any estimated health-literacy level.

### References

1. Sørensen K, Pelikan JM, Röthlin F, et al. Health literacy in Europe:
   comparative results of the European Health Literacy Survey (HLS-EU).
   *Eur J Public Health.* 2015;25(6):1053-1058.
   https://doi.org/10.1093/eurpub/ckv043
2. The HLS19 Consortium of the WHO Action Network M-POHL. *International
   Report on the Methodology, Results, and Recommendations of the European
   Health Literacy Population Survey 2019-2021 (HLS19).* Austrian National
   Public Health Institute; 2021.
   https://m-pohl.net/sites/m-pohl.net/files/inline-files/HLS19_International%20Report.pdf
3. Pelikan JM, Link T, Straßmayr C, et al. Measuring Comprehensive, General
   Health Literacy in the General Adult Population: The Development and
   Validation of the HLS19-Q12 Instrument in Seventeen Countries. *Int J
   Environ Res Public Health.* 2022;19(21):14129.
   https://doi.org/10.3390/ijerph192114129

## Indicator 4: employment context

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source items

- **Sources:** current work status from `q5_work_status` and, when conditionally
  displayed, time since last work from `q5b_last_worked`.
- **Classification:** contextual social determinant describing current work
  circumstances and reported recency of previous work.
- **Proposed retained outputs:** the detailed reported status, a conservative
  paid-work grouping, and the reported last-work category where applicable.

### Evidence and measurement limitations

Employment and working conditions are recognised social determinants of health.
They can shape income and resource security, time, control, exposures, access to
services, and opportunities to act on health information. Employment status
alone does not measure those mechanisms, however, and a particular status must
not be treated as intrinsically adverse.

The EU Labour Force Survey distinguishes employed, unemployed, and outside the
labour force using operational criteria. In particular, unemployment requires
being without work, actively seeking work, and available to start. The current
HEALIE item asks participants to select a self-described status and does not
measure job-search activity or availability. Its `unemployed` response must
therefore not be presented as an ILO- or Eurostat-derived labour-force
classification.

The item also does not measure job security, involuntary part-time work,
contract type, schedule control, occupational hazards, workplace support,
income loss, or whether a person combines paid work with studying or unpaid
care. Consequently, it cannot produce an employment-instability, precarious-
employment, or work-quality score. Because the question is single-select, it
also simplifies overlapping roles.

### Approved calculation and representation

For a participant currently reporting paid work:

```json
{
  "employment_context": {
    "assessment_status": "assessed",
    "current_status": "part_time",
    "paid_work_group": "current_paid_work"
  }
}
```

For a participant reporting a status outside current paid work and answering
the conditional follow-up:

```json
{
  "employment_context": {
    "assessment_status": "assessed",
    "current_status": "student",
    "paid_work_group": "not_currently_in_paid_work",
    "last_worked": "past_12_months"
  }
}
```

For a participant whose current reported status is `unemployed`, the original
last-work response may additionally be normalised into a duration category:

```json
{
  "employment_context": {
    "assessment_status": "assessed",
    "current_status": "unemployed",
    "paid_work_group": "not_currently_in_paid_work",
    "last_worked": "one_to_five_years",
    "unemployment_duration": "long_term"
  }
}
```

This normalisation applies only when the participant selected `unemployed`.
For students, homemakers, retired participants, or participants unable to work,
the same follow-up remains `last_worked` and must not be renamed unemployment
duration.

| `q5b_last_worked` value for an unemployed participant | `unemployment_duration` |
|---|---|
| `past_12_months` | `short_term` |
| `one_to_five_years` | `long_term` |
| `over_five_or_never` | `long_term_or_never_worked` |

The final category deliberately preserves the ambiguity of the source option:
the original questionnaire combines having worked more than five years ago
with never having worked. The export must not claim to distinguish these
states. The 12-month boundary is a conventional definition of long-term
unemployment, not a health-literacy cut-off.

The approved grouping is deliberately descriptive:

| `q5_work_status` value | `paid_work_group` | `last_worked` |
|---|---|---|
| `full_time` | `current_paid_work` | omitted |
| `part_time` | `current_paid_work` | omitted |
| `self_employed` | `current_paid_work` | omitted |
| `unemployed` | `not_currently_in_paid_work` | copied from visible `q5b_last_worked` |
| `homemaker` | `not_currently_in_paid_work` | copied from visible `q5b_last_worked` |
| `student` | `not_currently_in_paid_work` | copied from visible `q5b_last_worked` |
| `retired` | `not_currently_in_paid_work` | copied from visible `q5b_last_worked` |
| `unable_disability` | `not_currently_in_paid_work` | copied from visible `q5b_last_worked` |
| `other` | `other_or_unclassified` | omitted |
| `prefer_not_to_say` | omitted | omitted; status is `declined` |

`not_currently_in_paid_work` is not a risk flag and does not imply inactivity:
studying, homemaking, caregiving, and other unpaid work remain substantive
activities. The detailed status is retained so downstream systems do not have
to reconstruct it from the broad group.

### Prohibited inferences

This indicator must not independently produce:

- `employment_instability: true`;
- an ILO/Eurostat unemployment classification;
- precarious employment or poor working conditions;
- financial strain or poverty;
- disability severity or work capability beyond the reported category;
- limited health literacy; or
- inability to follow health recommendations.

Those constructs require direct measures. Household income and financial strain
must be derived from their own questions rather than inferred from work status.

### Deferred HEALIE decisions

- Relationships with Access, Understand, Appraise, or Apply.
- Weights and interactions with income, disability, transport, caregiving, or
  digital-access indicators.
- Personalisation rules concerning time, affordability, workplace context,
  service navigation, or feasibility.
- Any stronger effect assigned to longer unemployment. Existing studies have
  used long-term-unemployed samples and report substantial health-literacy
  needs, but do not establish a validated duration-response rule by which, for
  example, five years of unemployment should affect HEALIE more than one year.

### References

1. World Health Organization. *Determinants of health.* Employment and working
   conditions are identified among the determinants that can affect health.
   https://www.who.int/news-room/questions-and-answers/item/determinants-of-health
2. World Health Organization. *World report on social determinants of health
   equity.* 2025. https://www.who.int/publications/i/item/9789240107588
3. Eurostat. *Labour market - basic definitions.* The EU-LFS operationally
   distinguishes employment, unemployment, and being outside the labour force.
   https://ec.europa.eu/eurostat/web/european-statistics-learning-hub/statistics-for-beginners/labour-market-definitions
4. Dadaczynski K, Okan O, Messer M. Health literacy needs among unemployed
   persons: a qualitative study of perceived needs and implications for health
   promotion. *Int J Environ Res Public Health.* 2022;19(23):15514.
   https://doi.org/10.3390/ijerph192315514
5. FORESIGHT study: a health-promotion intervention for people with a history
   of long-term unemployment. The study supports attention to this population
   but does not establish a graded unemployment-duration effect on health
   literacy. *BMC Public Health.* 2025.

## Indicator 5: housing context and housing-related needs

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source items

- **Housing stability:** `q6a_housing_situation`.
- **Tenure context:** `q6b_tenure`.
- **Affordability experience:** `q6d_difficult_to_pay_housing` and
  `q6e_worry_housing_costs`.
- **Descriptive inputs not currently converted into risk indicators:** monthly
  housing cost (`q6c`), building type (`q7`), household size and bedrooms
  (`q8a` and `q8b`), residence length (`q9a`), and longest-residence postal code
  (`q9b`).

The participant-facing questions, response options, and original branching are
retained. Simplification occurs only in the derived HEALIE output.

### Evidence and measurement limitations

The current living-situation item closely follows the PRAPARE/AHC approach.
The AHC screening tool treats worry about losing housing or not having a steady
place to live as evidence of a housing-related social need. It does not require
a composite score combining tenure, building type, household size, postal code,
and residence duration.

Housing stability and affordability are related but distinct. Reported
difficulty paying rent or mortgage captures an experienced affordability
problem during the previous 12 months; current worry captures anticipated or
perceived financial pressure. Neither should be silently converted into the
other.

The monthly housing-cost amount cannot produce the Eurostat housing-cost
overburden indicator. Eurostat defines overburden as total housing costs, net of
housing allowances, exceeding 40% of total disposable household income, also
net of housing allowances. HEALIE has an income band rather than the exact
matched disposable-income measure and does not collect all components required
for that calculation.

Likewise, `household_size / bedrooms` is not the EU-SILC overcrowding measure.
The European definition depends on the number of rooms and the household's age,
sex, and couple composition. The current screener asks only for bedrooms and a
total number of residents. It therefore cannot validly label a household as
overcrowded. A persons-per-bedroom value could be calculated descriptively, but
no threshold is approved for HEALIE.

Tenure, building type, and short residence duration are not adverse conditions
by themselves. The postal-code response is potentially identifying location
data and is not needed in the compact HEALIE indicator payload unless a future,
governed area-level linkage is explicitly approved.

### Approved calculation and representation

The compact output preserves the two actionable constructs and only the
context needed to interpret them:

```json
{
  "housing_context": {
    "assessment_status": "assessed",
    "stability": "at_risk",
    "tenure": "rented",
    "affordability": {
      "payment_difficulty_past_12_months": true,
      "current_cost_worry": "very_worried",
      "need_identified": true
    }
  }
}
```

Housing stability is mapped directly:

| `q6a_housing_situation` | `stability` | `stability_need_identified` |
|---|---|---|
| `have_housing` | `stable` | `false` |
| `worried_losing` | `at_risk` | `true` |
| `no_housing` | `unhoused` | `true` |
| `prefer_not_answer` | omitted | omitted; `assessment_status` is `declined` |

Housing affordability is assessed only when the relevant source questions are
visible. `need_identified` is `true` when the participant reports payment
difficulty or reports being moderately or very worried about housing costs. It
is `false` only when all applicable affordability items are answered and none
meets that rule. Otherwise its assessment status must remain explicit rather
than treating missing data as no need.

`tenure` is copied as contextual information and is not itself a need flag.
Monthly cost, building type, raw household counts, residence duration, and
postal code are omitted from the compact HEALIE payload for now. They remain in
the source assessment and may be reconsidered for a separately governed
research or service-navigation purpose.

### Prohibited inferences

The current housing questions must not independently produce:

- an official Eurostat housing-cost-overburden classification;
- an EU-SILC overcrowding classification;
- homelessness from renting, occupying without rent, or short residence alone;
- poor housing quality from building type;
- neighbourhood deprivation from postal code without an approved external
  linkage and governance process;
- limited health literacy; or
- an overall vulnerability score.

### Deferred HEALIE decisions

- Relationships and weights for Access, Understand, Appraise, and Apply.
- Whether a housing need triggers resource navigation, affordability-sensitive
  recommendations, offline alternatives, or treatment-feasibility adaptations.
- Any use of exact cost, residence history, or area-level deprivation data.
- Research-mode derivation of a validated crowding or housing-cost measure if
  the necessary additional inputs are collected later.

### References

1. Centers for Medicare & Medicaid Services. *Accountable Health Communities
   Health-Related Social Needs Screening Tool.* Living Situation domain.
   https://www.cms.gov/files/document/ahcm-screeningtoolpdf.pdf
2. Centers for Medicare & Medicaid Services. *A Guide to Using the Accountable
   Health Communities Health-Related Social Needs Screening Tool.* The living-
   situation question was adapted from PRAPARE to identify people without
   housing or at risk of losing it.
   https://www.cms.gov/priorities/innovation/media/document/ahcm-screeningtool-companion
3. Eurostat. *Housing cost overburden rate.* Housing costs greater than 40% of
   total disposable household income, both net of housing allowances.
   https://ec.europa.eu/eurostat/databrowser/view/tespm140/default/table?lang=en
4. Eurostat. *Overcrowding rate by poverty status - EU-SILC survey.* The
   definition requires household composition and a minimum number of rooms.
   https://ec.europa.eu/eurostat/databrowser/view/tessi172/default/table?lang=en

## Indicator 6: reported health-coverage context

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source items

- **Source:** current self-reported health-coverage arrangement from
  `q10_health_coverage`.
- **Conditional source:** participant-entered description from
  `q10_health_coverage_other_text` when `other` is selected.
- **Classification:** healthcare-financing and navigation context, not a direct
  measure of realised access to healthcare and not a health-literacy score.
- **Approved retained output:** normalised coverage category and, where
  applicable, an explicit uncertainty or non-disclosure status.

The original participant-facing question, options, and conditional follow-up
are retained. The derived output must preserve what was reported without
silently translating it into a legal-entitlement determination.

### Evidence and measurement limitations

Insurance or coverage status and effective access to care are different
constructs. In Greece, Law 4368/2016 and its implementing decision established
access to public healthcare structures for uninsured people and vulnerable
groups. A participant selecting `no_coverage` therefore reports an important
financing and navigation context, but the answer does not prove that the person
has no access to any healthcare.

The reverse inference is also invalid. Reporting public, private, or combined
coverage does not demonstrate timely, affordable, geographically reachable, or
acceptable care. The 2025 Greece Country Health Profile reports major unmet
medical and dental needs related to costs, distance, and waiting times despite
the formal coverage framework. Coverage type must therefore not substitute for
direct questions about delayed care, medical costs, transport, or other unmet
needs.

The item also does not assess **health-insurance literacy**: understanding
benefits, eligibility, exclusions, copayments, referrals, reimbursement, or how
to navigate a coverage scheme. Research associates health-insurance literacy
with some healthcare-utilisation outcomes, but that construct requires its own
instrument or direct items and cannot be inferred from selecting `not_sure` or
a particular coverage type.

Finally, `private_only` and `no_coverage` are self-descriptions rather than
verified administrative classifications. A respondent may not know all public
entitlements or may interpret “coverage” as the scheme they normally use.

### Comparison with established screeners and implementations

Comparable systems do not handle coverage in one uniform way:

- **PRAPARE** includes primary insurance as a standardised descriptive field.
  Its interoperable HL7/LOINC representation records the selected insurance
  category (for example, Medicaid in the US implementation). PRAPARE's action
  guidance discusses lack of insurance or underinsurance as a possible barrier
  requiring support; it does not establish that every insurance category maps
  to a universal graded social-risk score.
- **CMS Accountable Health Communities HRSN Tool** does not use insurance type
  as one of its five scored core HRSN domains. It was designed to screen people
  across insurance statuses. Its operational HRSN outputs focus on housing,
  food, transportation, utilities, and interpersonal safety.
- **EHR HRSN implementations** commonly turn answers in those directly
  actionable domains into domain-specific need/no-need statuses. Insurance
  information is often already represented as administrative or demographic
  context rather than being inferred from the HRSN score.
- **Greek digital public services** maintain a separate authoritative
  insurance-capacity register. This reinforces that a brief self-report item in
  HEALIE should not pretend to verify legal coverage or eligibility.

The consistent pattern relevant to HEALIE is therefore to preserve reported
coverage as a category, while deriving an access need from direct evidence of
unmet care or navigation difficulty rather than coverage type alone.

### Approved calculation and representation

For an assessed response:

```json
{
  "health_coverage_context": {
    "assessment_status": "assessed",
    "reported_coverage": "public_only"
  }
}
```

The mapping is intentionally direct:

| `q10_health_coverage` | Derived representation |
|---|---|
| `public_only` | `reported_coverage: "public_only"` |
| `private_only` | `reported_coverage: "private_only"` |
| `both_public_private` | `reported_coverage: "both_public_private"` |
| `no_coverage` | `reported_coverage: "none_reported"` |
| `other` | `reported_coverage: "other"` |
| `not_sure` | `assessment_status: "uncertain"` |
| `prefer_not_to_say` | `assessment_status: "declined"` |

No `healthcare_access_barrier` boolean is derived from Q10 alone. Direct access
needs will be represented later from the relevant items—for example, delayed
care because of cost, difficulty paying medical bills, or a transport barrier.

The free-text `other` answer remains available for immediate validation or
participant-facing workflow if required, but is not included verbatim in the
compact HEALIE payload. Retaining arbitrary free text would conflict with the
current data-minimisation goal and could introduce unexpected personal or
health information. A future controlled mapping may normalise recurring
answers if a justified category is identified.

### Prohibited inferences

Q10 must not independently produce:

- `healthcare_access_barrier: true` or `false`;
- legally verified insured or uninsured status;
- eligibility for a particular Greek public service or benefit;
- inability to obtain healthcare from `none_reported` alone;
- adequate access from public, private, or combined coverage;
- health-insurance literacy;
- general health literacy; or
- a preference for public or private healthcare information.

### Deferred HEALIE decisions

- Whether reported coverage should affect service-navigation content or the
  relevance of public/private resource links.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Whether HEALIE needs a separate, directly measured healthcare-navigation or
  health-insurance-literacy construct.
- Country-specific entitlement rules and their maintenance, governance, and
  versioning.

### References

1. Hellenic Ministry of Health. *Access of uninsured people to the public
   health system.* Law 4368/2016 and Joint Ministerial Decision
   A3(g)/GP/oik.25132/4-4-2016 established access to public health structures
   for uninsured people and vulnerable groups.
   https://www.moh.gov.gr/articles/health/anaptyksh-monadwn-ygeias/3999-prosbash-twn-anasfalistwn-sto-dhmosio-systhma-ygeias
2. OECD and European Observatory on Health Systems and Policies. *Greece:
   Country Health Profile 2025.* State of Health in the EU; 2025.
   https://www.oecd.org/en/publications/country-health-profile-2025-country-notes_c0e8b8be-en/greece_9ca0bb52-en.html
3. Eurostat. *Unmet needs for medical care in 2024.* Unmet need encompasses
   financial reasons, waiting lists, and distance from providers.
   https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20250820-2
4. Yagi BF, Luster JE, Scherer AM, Farron MR, Smith JE, Tipirneni R.
   Association of health insurance literacy with health care utilization: a
   systematic review. *J Gen Intern Med.* 2022;37:375-389.
   https://doi.org/10.1007/s11606-021-06819-0
5. PRAPARE. *Action Toolkit, Chapter 9: Insurance Status.*
   https://prapare.org/wp-content/uploads/2021/10/PRAPARE-Action-Toolkit-Chapter-9.pdf
6. HL7. *SDOH Clinical Care QuestionnaireResponse PRAPARE Example.* The
   interoperable example represents primary insurance as a coded response.
   https://hl7.org/fhir/us/sdoh-clinicalcare/STU2.2/QuestionnaireResponse-SDOHCC-QuestionnaireResponsePRAPAREExample.html
7. Centers for Medicare & Medicaid Services. *A Guide to Using the AHC HRSN
   Screening Tool.* The tool screens people across insurance types and defines
   five core HRSN domains separately from insurance status.
   https://www.cms.gov/priorities/innovation/media/document/ahcm-screeningtool-companion
8. Gov.gr. *Check the status of your insurance capacity.*
   https://www.gov.gr/en/org/efka/iatropharmakeutike-perithalpse/asphalistike-ikanoteta

## Indicator 7: household home-internet context

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source item

- **Source:** `q11_internet` — whether the participant or any other household
  member has internet access at the current house, apartment, or mobile home.
- **Classification:** household-level connectivity context and one component of
  the digital determinants of health.
- **Approved retained output:** household home-internet availability with an
  explicit assessment status.

The original item and its housing-dependent visibility rule are retained.

### Source and comparison with established measures

The wording originates from the US American Community Survey (ACS), where it is
used as a household ICT-access measure. The full ACS distinguishes paid access,
access without payment, no home access, and connection types such as mobile
data, fixed broadband, and satellite. HEALIE's binary adaptation captures only
whether any household member has access at the dwelling.

This differs from direct-to-person digital-health screening. Broad HRSN tools
such as the CMS AHC core screen do not treat household internet access as one of
their five scored core needs. Dedicated digital-inclusion assessments commonly
separate device availability, connectivity quality, affordability, skills,
support, accessibility, and actual use. WHO/Europe likewise identifies internet
access, connectivity, device/software availability, and digital literacy as
important but distinct digital determinants.

HEALIE's later six-item DDoH module follows this multidimensional approach by
asking directly about a suitable device, reliable connectivity, affordability,
accessibility, support, and privacy/trust in the context of online health
information and services. Q11 should therefore remain a narrow household
context variable rather than duplicate or override that module.

### Evidence and measurement limitations

A `true` response does not establish that the participant personally has:

- permission or practical opportunity to use the connection;
- a suitable device;
- reliable or sufficiently fast connectivity;
- affordable continued access;
- privacy for sensitive health activities;
- accessible digital content;
- digital skills or support; or
- experience using online health services.

The connection may belong to another household member. Conversely, no internet
at the dwelling does not prove total digital exclusion: the participant may use
mobile data, public access, work, another household, or another location.

Because Q11 is shown only to participants who currently have housing or are
worried about losing it, its absence for an unhoused participant means
`not_applicable` to the dwelling-specific question—not `false` and not
`not_assessed`. Personal device and connectivity access can still be assessed
by the later DDoH items.

Household internet access is nevertheless a relevant contextual determinant.
WHO/Europe identifies internet access and connectivity among high-priority
digital determinants, and official Greek and Eurostat household ICT surveys
continue to measure home access. In 2025, household access remained below the
EU average in Greece, with an additional urban-rural gap. Population prevalence
does not, however, validate a personal health-literacy or digital-exclusion
score from this single item.

### Approved calculation and representation

When Q11 is visible and answered:

```json
{
  "home_internet_context": {
    "assessment_status": "assessed",
    "household_access": true
  }
}
```

When the dwelling-specific question is hidden because the participant reports
having no housing:

```json
{
  "home_internet_context": {
    "assessment_status": "not_applicable"
  }
}
```

No global `digital_exclusion` or `digital_access_need` flag is derived from Q11
alone. The later DDoH indicators determine personal constraints relevant to
online health information and services. Q11 may remain available as supporting
context so the two levels can be distinguished—for example, household access
may be present while the participant reports unreliable personal connectivity.

### Prohibited inferences

Q11 must not independently produce:

- personal internet access or non-access;
- broadband availability or connection quality;
- device availability;
- digital literacy or eHealth literacy;
- ability or willingness to use online health services;
- general health literacy;
- `digital_exclusion: true` or `false`; or
- absence of a digital need merely because another household member has
  internet access.

### Deferred HEALIE decisions

- Whether household-level access materially improves personalisation after the
  six direct DDoH indicators are available.
- Whether Q11 can eventually be omitted from the compact HEALIE payload as
  redundant while remaining in the source questionnaire for fidelity.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Offline, low-bandwidth, printable, assisted, or alternative-channel
  adaptations triggered by the combined DDoH profile.

### References

1. United States Census Bureau. *American Community Survey — Informational Copy
   (2025).* Computer and Internet Use questions 10-12.
   https://www2.census.gov/programs-surveys/acs/methodology/questionnaires/2025/quest25.pdf
2. World Health Organization Regional Office for Europe. *Addressing health
   determinants in a digital age: project report.* 2024.
   https://www.who.int/europe/publications/i/item/WHO-EURO-2024-10917-50689-76724
3. WHO/Europe. *New WHO and London School of Economics study identifies key
   digital factors affecting health.* 2 December 2024.
   https://www.who.int/europe/news/item/02-12-2024-new-who-and-london-school-of-economics-study-identifies-key-digital-factors-affecting-health
4. Hellenic Statistical Authority. *Survey on the Use of Information and
   Communication Technologies by Households and Individuals: 2025.*
5. Eurostat. *Internet access in households, 2025.* Household access and degree
   of urbanisation.
   https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/108644.pdf

## Indicator 8: self-reported functional and disability context

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source item

- **Source:** the six rows of `q12_disability` covering hearing, vision,
  cognition, mobility, self-care, and independent living/errands.
- **Classification:** participant-reported functional difficulty across six
  domains; useful as accessibility and daily-function context.
- **Approved retained outputs:** the domain-specific boolean responses and a
  conservative `any_reported_difficulty` summary.

The participant-facing six-question set is retained as close to its source as
possible. All six rows must be complete before an assessed output is produced.

### Source and comparison with established measures

Q12 is the **American Community Survey six-item disability set (ACS-6)**. The
US Census Bureau and US health surveys use it to identify six disability types:
hearing, vision, cognition, ambulatory, self-care, and independent living. For
ACS population reporting, a `yes` response to any item is classified as having
a disability.

The ACS-6 is also used in the US Behavioral Risk Factor Surveillance System and
is treated as a minimum standard for disability data collection. Comparable
clinical interoperability systems represent functional or disability
assessment results as structured observations rather than inferring them from
diagnoses alone. This supports retaining the six domains separately.

The **Washington Group Short Set on Functioning (WG-SS)** is related but not
interchangeable. It uses graded response options such as no difficulty, some
difficulty, a lot of difficulty, and cannot do at all, and includes
communication rather than the ACS independent-living/errands item. HEALIE's
binary ACS-6 responses must not be described or scored as WG-SS results.

### Evidence and measurement limitations

The items report functional difficulties; they do not identify an underlying
diagnosis, cause, duration, treatment, assistive technology, preferred
accommodation, or exact severity. A `yes` response should therefore be retained
in the domain in which it was reported rather than converted into a medical
condition.

The binary ACS-6 is useful for identifying broad population groups but loses
the functional continuum captured by graded instruments. Counting positive
domains would measure the number of domains reported, not the severity of
disability. A participant with one major access requirement must not be treated
as having a lesser need than someone reporting several milder limitations.

The cognition item asks about serious difficulty concentrating, remembering,
or making decisions because of a physical, mental, or emotional condition. It
is not a cognitive test and does not diagnose mild cognitive impairment,
dementia, intellectual disability, or a specific mental-health condition. It
also cannot establish limited health literacy.

Similarly, difficulty doing errands alone can arise from mobility, cognition,
anxiety, access barriers, lack of assistance, or other causes. It does not by
itself establish a transportation need or inability to attend healthcare.

Most importantly for HEALIE, a reported functional difficulty identifies an
area in which accessibility should be considered; it does not reveal the
participant's preferred interface or accommodation. For example, serious
vision difficulty does not establish whether the person prefers screen-reader
output, magnification, audio, high contrast, or assistance. Those preferences
should be offered or directly elicited rather than imposed.

### Approved calculation and representation

```json
{
  "functional_access_context": {
    "assessment_status": "assessed",
    "any_reported_difficulty": true,
    "reported_domains": {
      "hearing": false,
      "vision": true,
      "cognition": false,
      "mobility": false,
      "self_care": false,
      "independent_living": false
    },
    "source_measure": "acs_6"
  }
}
```

`any_reported_difficulty` is the logical OR of the six completed responses. It
is a summary of the source measure—not an overall severity score. The detailed
domains remain essential because they have different accessibility and
real-world implications.

If the checklist is incomplete, the result is `not_assessed`; unanswered rows
must not become `false`. The current questionnaire requires completion of every
row, so this state should normally be returned only for incomplete or legacy
payloads.

### Prohibited inferences

Q12 must not independently produce:

- a medical diagnosis or cause of disability;
- a disability percentage, severity score, or benefit eligibility result;
- a WG-SS classification;
- cognitive impairment or dementia;
- limited health literacy;
- inability to understand, appraise, or apply health information;
- a specific assistive technology or presentation preference;
- a transportation barrier from the mobility or errands item; or
- inability to live independently.

### Deferred HEALIE decisions

- Relationships and weights for Access, Understand, Appraise, and Apply.
- Rules for offering—but not forcing—visual, auditory, cognitive, motor, or
  navigation accommodations.
- Whether HEALIE should directly ask for accessibility preferences after a
  reported domain difficulty.
- Interactions with the later DDoH accessibility item and the self-reported
  cognition screen.
- Interoperable coding of domain observations in the ontology and FHIR-facing
  output.

### References

1. United States Census Bureau. *How Disability Data are Collected from the
   American Community Survey.*
   https://www.census.gov/topics/health/disability/guidance/data-collection-acs.html
2. Centers for Disease Control and Prevention. *A Data Users' Guide to the
   Disability Questions Included in the Behavioral Risk Factor Surveillance
   System.* 2018.
   https://www.cdc.gov/brfss/data_documentation/pdf/BRFSS_Data_Users_Guide_on_Disability_Questions_2018-508.pdf
3. United States Census Bureau. *2022 American Community Survey Content Test
   Evaluation Report: Disability.* 2023.
   https://www.census.gov/content/dam/Census/library/working-papers/2023/acs/2023_Steinweg_01.pdf
4. Washington Group on Disability Statistics. *Washington Group Short Set on
   Functioning.*
   https://www.washingtongroup-disability.com/question-sets/wg-short-set-on-functioning-wg-ss/
5. HL7 US Core. *Screening and Assessments.* Guidance for representing
   functional status, disability status, mental/cognitive status, and SDoH
   assessments.
   https://build.fhir.org/ig/HL7/US-Core/screening-and-assessments.html

## Indicator 9: healthcare-language proficiency context

**Decision status:** Approved conceptually; derived-output implementation
pending.

### Construct and source item

- **Source:** `q13_local_language_proficiency`.
- **Construct:** self-rated ability to **speak** the primary language used in
  the participant's healthcare setting.
- **Classification:** language-access and communication context; not a measure
  of health literacy, education, intelligence, migration status, or overall
  literacy.
- **Approved retained outputs:** the reported proficiency category and a
  conservative language-access status.

The original four response options—`very_well`, `well`, `not_well`, and
`not_at_all`—are retained.

### Source and comparison with established measures

The four-category response scale follows established US Census, HHS, SAMHSA,
PhenX, and LOINC language-proficiency measures. In US Census analyses, people
who report speaking English less than `very well` are commonly grouped as
having limited English proficiency. That binary threshold is useful for
population reporting but should not be treated as a universal clinical test or
as proof that every person selecting `well` requires the same service.

PRAPARE takes a complementary approach: it records the language in which the
participant is most comfortable speaking. Healthcare and EHR implementations
often preserve preferred language as a coded field so that communication and
interpretation services can use it directly.

HEALIE currently asks about proficiency in the healthcare setting's primary
language but does **not** ask which language that is or which language the
participant prefers. It can therefore identify a possible communication
constraint but cannot choose a translation language. The item also asks only
about speaking; it does not directly measure understanding spoken information,
reading, writing, or comprehension of health terminology.

### Evidence and measurement limitations

Language barriers are associated with difficulties identifying services,
securing appointments, communicating with professionals, understanding
instructions, and following post-appointment care. These associations support
treating Q13 as relevant to Access, Understand, and Apply in later HEALIE
modelling.

Language proficiency and health literacy remain distinct. A person may have
high health literacy in a preferred language while facing a barrier in the
healthcare setting's language. Conversely, speaking the local language very
well does not demonstrate the ability to understand, appraise, or apply complex
health information.

Self-rated proficiency is also context dependent. Speaking socially, discussing
symptoms, understanding risk explanations, reading medication information, and
making a shared decision place different demands on language. The result should
therefore guide an offer of language support, not a judgement about personal
capability.

### Approved calculation and representation

```json
{
  "language_access_context": {
    "assessment_status": "assessed",
    "speaking_proficiency": "not_at_all",
    "language_support_indicated": true
  }
}
```

The approved mapping is:

| `q13_local_language_proficiency` | `speaking_proficiency` | `language_support_indicated` |
|---|---|---|
| `very_well` | `very_well` | `false` |
| `well` | `well` | `false` |
| `not_well` | `not_well` | `true` |
| `not_at_all` | `not_at_all` | `true` |

`language_support_indicated` is always a boolean. The original four-category
response remains available in `speaking_proficiency`, so `not_well` and
`not_at_all` are not collapsed even though both cross the conservative support
threshold. The boolean indicates that language support should be offered; it
does not prescribe a particular service or imply that support is unwanted.

The threshold is deliberately set at `not_well` rather than the broader US
Census population convention of “less than very well.” A participant selecting
`well` may still choose multilingual or plain-language options, but Q13 alone
does not mark support as indicated. A support response should never reduce the
amount or quality of information available.

If the required item is missing, the result is `not_assessed`; it must not be
treated as `very_well` or as absence of a barrier.

### Prohibited inferences

Q13 must not independently produce:

- low or high health literacy;
- general literacy, reading ability, or educational attainment;
- intelligence or cognitive ability;
- migration, citizenship, ethnic, or cultural identity;
- a preferred language or requested interpreter language;
- inability to consent or participate in shared decision-making;
- a requirement to simplify or withhold clinical detail; or
- automatic use of unreviewed machine translation for clinical information.

### Deferred HEALIE decisions

- Relationships and weights for Access, Understand, Appraise, and Apply.
- Whether a separate preferred-language item is needed for actionable
  multilingual personalisation.
- Whether the participant should be asked directly about interpreter,
  translated-content, audio, or bilingual-support preferences.
- Governance and human review requirements for translated clinical content.
- Interaction with DDoH accessibility, education, and directly measured health
  literacy.

### References

1. LOINC. *68503-2: How well do you speak English [SAMHSA]* and answer list
   `Very well / Well / Not well / Not at all`.
   https://loinc.org/68503-2
2. LOINC. *93025-5: PRAPARE.* Includes the participant's preferred or most
   comfortable spoken language.
   https://loinc.org/93025-5/panel
3. Twersky SE, Jefferson R, Garcia-Ortiz L, Williams E, Pina C. The impact of
   limited English proficiency on healthcare access and outcomes in the US: a
   scoping review. 2024.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC10855368/
4. Pandey M, Maina RG, Amoyaw J, et al. Impacts of English language proficiency
   on healthcare access, use, and outcomes among immigrants: a qualitative
   study. *BMC Health Serv Res.* 2021;21:741.
   https://doi.org/10.1186/s12913-021-06750-4
5. Al Shamsi H, Almutairi AG, Al Mashrafi S, Al Kalbani T. Implications of
   language barriers for healthcare: a systematic review. *Oman Med J.*
   2020;35(2):e122. https://doi.org/10.5001/omj.2020.40

## Indicator 10: family and partnership context

### Decision

Retain both Q14 items in the participant assessment and expose their answers as
context, not as a scored need or health-literacy deficit. Marital or partnership
status and single-parent status describe different constructs and must remain
separate.

### Source and comparison with established measures

Marital status is a conventional demographic variable in population surveys.
Single-parent household status describes household composition and possible
care responsibilities rather than legal partnership status. A person may be
unmarried and not a single parent, or legally married while parenting without a
partner in the household; one field cannot safely be inferred from the other.

Major health-related social-needs screeners focus primarily on directly
actionable needs such as food, housing, transport, utilities, and personal
safety. They do not generally treat marital status itself as a positive screen.
European household statistics similarly use lone-parent status to analyse
population-level living conditions and socioeconomic inequalities, not as an
individual diagnostic or vulnerability score.

### Evidence and measurement limitations

Partnership and family structure have been associated with health and health
literacy in observational studies, but results vary by population and context.
For example, one study of mothers found partnership status among several
predictors of health literacy, while another study reported no significant
marital-status difference and higher measured health literacy among single
parents. These findings do not support a universal direction, cutoff, or causal
rule for an individual participant.

Single-parent households may face time, childcare, financial, and logistical
constraints that affect the feasibility of acting on health information.
However, those constraints should be established through direct questions or
the relevant economic, transport, and social-support indicators. They must not
be presumed solely from family structure.

### Approved calculation and representation

```json
{
  "family_context": {
    "assessment_status": "assessed",
    "marital_status": "divorced",
    "single_parent": true
  }
}
```

`marital_status` preserves the questionnaire category:

- `now_married`;
- `widowed`;
- `divorced`;
- `separated`;
- `never_married`;
- `living_with_partner`; or
- `prefer_not_to_say`.

`single_parent` is the direct boolean response to Q14b. It is not derived from
`marital_status`.

If either required item is absent, `assessment_status` is `not_assessed`. A
marital response of `prefer_not_to_say` is an assessed response and is retained
as such; it must not be converted to missing data. No combined family-risk flag
or score is calculated.

### Personalisation role

The context may later help HEALIE offer practical, participant-controlled
adaptations—for example concise action plans, flexible pacing, save-and-return,
or resources compatible with caring responsibilities. It should not silently
reduce content, assume low capacity, or make support choices on the person's
behalf. Directly reported needs remain authoritative.

### Prohibited inferences

Q14 must not independently produce:

- low or high health literacy;
- social isolation, loneliness, or availability of support;
- financial hardship, childcare difficulty, or caregiving burden;
- a mental-health, safety, or intimate-partner-violence result;
- legal relationship status inferred from cohabitation, or cohabitation inferred
  from legal status;
- a `single_parent_risk` or general vulnerability label; or
- different clinical information or quality of care.

### Deferred HEALIE decisions

- Whether marital status has a necessary personalisation use beyond research
  and descriptive context.
- Which optional interface adaptations, if any, should be offered to a person
  who reports being a single parent.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Interaction with directly measured household income, transport, social
  support, and unmet-needs indicators.
- Whether future research-mode exports should separate legal marital status,
  cohabitation, parenting, and caregiving more precisely.

### References

1. Sántha Á. The sociodemographic determinants of health literacy in a
   population of mothers in Hungary. 2021. PMID: 34063905.
   https://pubmed.ncbi.nlm.nih.gov/34063905/
2. Asil EU, et al. The relationship between parental health literacy and
   primary-school children's health. 2025.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11844121/
3. von der Lippe E, Rattay P. Association of partner, parental, and employment
   statuses with self-rated health among German women and men. 2016.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC5757937/

## Indicator 11: transportation access context

### Decision

Retain usual travel mode as contextual information and replace the current
boolean transportation-barrier item with the more informative PRAPARE-style
domain distinction. Only the reported barrier item determines whether a
transportation access barrier exists.

### Source and comparison with established measures

PRAPARE distinguishes transportation that prevented medical appointments or
obtaining medication from transportation that prevented non-medical meetings,
work, appointments, or obtaining daily necessities. Both may apply. The AHC
adaptation uses a similar distinction, whereas the Health Leads recommended
item concentrates on having to go without healthcare because transportation
was unavailable.

HEALIE will preserve the wider PRAPARE-style distinction because it remains
short, identifies an actionable access problem, and distinguishes direct
healthcare access from broader daily-living access. The current 12-month recall
period is retained for consistency with the adapted screener.

### Questionnaire representation

Q15a remains the participant's usual travel method during the previous week.
Q15b becomes a checklist asking whether lack of reliable transportation kept
the participant from:

- medical appointments or obtaining medicines;
- work, meetings, appointments, or things needed for daily living;
- neither; or
- answering the question.

The two barrier categories may be selected together. `No transportation-related
difficulties` and `Prefer not to answer` are each exclusive of every other
choice.

### Approved calculation and representation

```json
{
  "transportation_access_context": {
    "assessment_status": "assessed",
    "usual_travel_mode": "bus_coach_minibus",
    "barrier_reported": true,
    "healthcare_access_affected": true,
    "daily_living_access_affected": false
  }
}
```

The mapping is:

- either positive Q15b domain makes `barrier_reported` `true`;
- the healthcare category controls `healthcare_access_affected`;
- the non-medical/daily-living category controls
  `daily_living_access_affected`;
- an exclusive `none` response makes all three booleans `false`; and
- an exclusive declined response sets `assessment_status` to `declined` and
  all three derived booleans to `null`.

Q15a supplies `usual_travel_mode` but does not affect any of the three barrier
booleans. If `other` is selected, the exported category is `other`; verbatim
free text is not included in the standard HEALIE indicator payload.

If a required non-declined response is absent or internally inconsistent,
`assessment_status` is `not_assessed`; missing information must not be converted
to absence of a barrier.

### Personalisation and Sørensen model role

A reported barrier is directly relevant to the **Access** dimension because it
can prevent access to healthcare, medication, work, services, or necessities.
Potential later adaptations include remote-access options, flexible scheduling,
locally available resources, and information about transport support. These
adaptations must be offered rather than assumed.

Q15 does not directly measure the ability to Understand, Appraise, or Apply
health information. Relationships and weights across the four dimensions remain
deferred.

### Prohibited inferences

Q15 must not independently infer:

- a transportation barrier from walking, cycling, public transport, working
  from home, or not travelling during the reference week;
- vehicle ownership, affordability, disability, rurality, or income;
- inability to attend a future appointment;
- low health literacy or lack of motivation;
- the reason transportation was unreliable; or
- a preferred transport intervention.

### Deferred HEALIE decisions

- The exact resources and interface adaptations offered for healthcare versus
  daily-living transportation barriers.
- Whether later versions should ask separately about cost, physical
  accessibility, geographic availability, safety, or service reliability.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Interaction with disability, digital access, rurality, and healthcare-access
  indicators.

### References

1. National Association of Community Health Centers. *PRAPARE Assessment
   Tool.* https://prapare.org/wp-content/uploads/2021/10/PRAPARE-English.pdf
2. Health Leads. *Social Needs Screening Toolkit.* 2018.
   https://healthleadsusa.org/wp-content/uploads/2023/05/Screening_Toolkit_2018.pdf
3. Wu X. *Lack of Reliable Transportation for Daily Living Among Adults:
   United States, 2022.* Medical Expenditure Panel Survey Statistical Brief
   558. 2024. https://www.ncbi.nlm.nih.gov/books/n/mepssb/stat558/
4. Centers for Disease Control and Prevention. Percentage of adults who lacked
   reliable transportation for daily living, National Health Interview Survey,
   2022. *MMWR.* 2024;73:152.
   https://www.cdc.gov/mmwr/volumes/73/wr/mm7307a4.htm

## Indicator 12: unmet material needs, healthcare affordability, and financial strain

### Decision

Preserve the original Q16 questionnaire sequence and conditional logic, but
export its results as three distinct constructs:

1. reported unmet material needs;
2. healthcare affordability consequences; and
3. current financial worry.

Do not collapse these constructs into a single vulnerability flag or score.

### Source and comparison with established measures

The opening item is the PRAPARE unmet-needs item, registered as LOINC
`93031-3`. It asks whether the participant or a family member living with them
was unable to obtain specified necessities when they were really needed during
the previous year. It is a domain checklist rather than a food-insecurity scale.

The subsequent items assess different experiences: difficulty paying medical
bills, care delayed because of cost, housing-cost worry, and worry about normal
monthly bills. Similar items appear in health-related social-needs research and
US national health surveys, but together they do not constitute one validated
summed scale.

Food or healthy-food selection in this checklist must not be labelled as a
positive Hunger Vital Sign result. Hunger Vital Sign uses two different
household food-security statements and a validated response rule.

### Approved calculation and representation

```json
{
  "material_needs_context": {
    "assessment_status": "assessed",
    "any_unmet_need": true,
    "unmet_domains": [
      "food",
      "healthy_food",
      "healthcare"
    ]
  },
  "healthcare_affordability_context": {
    "assessment_status": "assessed",
    "medical_bill_payment_problem": true,
    "care_delayed_due_to_cost": false
  },
  "financial_strain_context": {
    "assessment_status": "assessed",
    "housing_cost_worry": "moderately_worried",
    "monthly_bill_worry": "very_worried"
  }
}
```

The supported `unmet_domains` are:

- `food`;
- `healthy_food`;
- `healthcare`; and
- `phone`.

`any_unmet_need` is `true` when at least one domain is selected and `false`
only when the checklist is validly completed with no positive domain. It must
not be inferred as `false` from a missing or declined response.

The healthcare-affordability booleans preserve the direct answers to Q16a and
Q16b. The two worry fields preserve all four ordered response categories:
`very_worried`, `moderately_worried`, `not_too_worried`, and `not_worried`.
No cutoff or combined financial-strain score is currently calculated.

If Q16 is declined, `material_needs_context.assessment_status` is `declined`,
`any_unmet_need` is `null`, and `unmet_domains` is empty. The empty array is not
evidence of no unmet need unless the status is `assessed`.

### Approved visibility and clearing logic

- Any selected unmet-need domain makes all four original follow-up questions
  visible.
- Selecting only `I choose not to answer` hides the follow-ups.
- The declined item is exclusive of every need domain.
- Changing to the declined response clears previously entered follow-up
  answers.
- A selected need does not determine or pre-fill any follow-up response.
- Every visible required follow-up must be completed before the participant can
  continue.

Although visibility is triggered by any reported need, the follow-ups remain
independent constructs. For example, reported food need does not imply unpaid
medical bills, and phone need does not imply housing-cost worry.

### Personalisation and Sørensen model role

The results primarily describe constraints on **Access** to resources and the
practical feasibility of **Apply**. Medical-cost delay is a direct reported
healthcare-access barrier. Financial worry may affect attention, appraisal, and
capacity to act, but dimension mappings and weights remain deferred.

HEALIE may later use these indicators to prioritise affordable, feasible, and
locally accessible options. It must preserve the quality and completeness of
health information and should offer adaptations rather than silently impose
them.

### Prohibited inferences

Q16 must not independently produce:

- low health literacy or low cognitive ability;
- a diagnosis of food insecurity based solely on this PRAPARE checklist;
- poverty status or household income;
- medical debt amount or severity;
- a causal relationship between a selected unmet need and a follow-up answer;
- inability or unwillingness to follow medical advice; or
- one combined `social_risk`, `financial_vulnerability`, or priority score.

### Deferred HEALIE decisions

- Relationships and weights for Access, Understand, Appraise, and Apply.
- Whether a validated food-security instrument should be added in a research
  or service-specific version.
- Whether worry categories should later support a separately validated
  financial-strain rule.
- Resource-routing rules for each unmet domain and healthcare-affordability
  consequence.
- Interaction with household income, housing affordability, transport, health
  coverage, and digital access.

### References

1. LOINC. *93031-3: Have you or any family members you live with been unable to
   get any of the following when it was really needed in past 1 year
   [PRAPARE].* https://loinc.org/93031-3
2. HL7 International. *SDOH Clinical Care PRAPARE Questionnaire.*
   https://hl7.org/fhir/us/sdoh-clinicalcare/en/Questionnaire-SDOHCC-QuestionnairePRAPARE.html
3. SIREN. *Food Insecurity Questions.*
   https://sirenetwork.ucsf.edu/food-insecurity-questions-0
4. Pariyo GW, et al. Standardizing social determinants of health data: a
   proposal for a comprehensive screening tool to address health equity—a
   systematic review. *Health Affairs Scholar.* 2024;2(12):qxae151.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11642620/

## Indicator 13: social contact frequency

### Decision

Preserve the ordered Q17 contact-frequency response as social-connection
context. Do not derive social isolation, loneliness, inadequate support, or a
binary social-risk result from this single item.

### Source and comparison with established measures

Q17 is the PRAPARE social-integration item registered as LOINC `93029-7`. The
source paper reproduces its frequency categories but does not prescribe an
indicator calculation or cutoff. This contrasts with the paper's explicit
scoring instructions for measures such as PHQ-2 and physical activity.

PRAPARE's separate cumulative risk-tally methodology assigns one tally to every
frequency of five or fewer contacts per week and zero only for more than five.
HEALIE will not import that threshold. It is a component of a broader PRAPARE
risk tally, not a validated diagnosis of isolation, and it would categorise
three to five meaningful interactions per week as risk without considering
network size, perceived sufficiency, or available support.

Validated social-isolation measures such as the LSNS-6 use several questions
about family and friends, contact, network size, and available support. Q17 is
not equivalent to those instruments.

### Approved calculation and representation

```json
{
  "social_connection_context": {
    "assessment_status": "assessed",
    "contact_frequency": "1_2_week"
  }
}
```

The preserved ordered categories are:

- `lt_once_week`;
- `1_2_week`;
- `3_5_week`; and
- `6plus_week`.

The code `6plus_week` is the unambiguous implementation of the source category
“more than 5 times a week.” A declined response sets `assessment_status` to
`declined` and `contact_frequency` to `null`. A missing required response is
`not_assessed`.

### Construct boundaries

Q17 measures reported frequency of contact with people the participant cares
about and feels close to. It does not directly measure:

- subjective loneliness;
- satisfaction with the amount of contact;
- social-network size or diversity;
- practical, informational, or emotional support;
- neighbourhood cohesion; or
- whether the participant wants more contact.

Q18 neighbourhood support remains a separate construct and must not be used to
fill or overwrite Q17.

### Personalisation and Sørensen model role

Trusted social contacts could later facilitate Access, Appraise, and Apply, but
Q17 alone does not establish that the participant wants or can use another
person's support. No dimension weights or automatic social-support adaptations
are assigned now.

### Prohibited inferences

Q17 must not independently produce:

- `socially_isolated` or `lonely`;
- a social-support deficit;
- depression, anxiety, cognitive decline, or vulnerability;
- a preferred communication channel;
- permission to involve relatives, friends, or caregivers; or
- a PRAPARE or combined social-risk tally.

### Deferred HEALIE decisions

- Whether a direct loneliness item or validated multi-item social-network
  measure is required in a future research version.
- Whether and how participants may explicitly opt into support-person
  involvement.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Joint interpretation with Q18, family context, and mental-health screens.

### References

1. LOINC. *93029-7: How often do you see or talk to people that you care about
   and feel close to [PRAPARE].* https://loinc.org/93029-7
2. National Association of Community Health Centers. *PRAPARE Risk Tally
   Scoring Methodology.* 2021.
   https://prapare.org/wp-content/uploads/2021/10/PRAPARE-Risk-Tally-Scoring-Methodology_2021.pdf
3. National Academies of Sciences, Engineering, and Medicine. *Social
   Isolation and Loneliness in Older Adults: Opportunities for the Health Care
   System.* 2020. https://doi.org/10.17226/25663
4. Donovan NJ, Blazer D. Social isolation and loneliness in older adults:
   review and commentary of a National Academies report. *Am J Geriatr
   Psychiatry.* 2020;28(12):1233-1244.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC7437541/

## Indicator 14: perceived neighbourhood support

### Decision

Preserve the ordered Q18 response as perceived neighbourhood-support context.
Do not derive a neighbourhood-cohesion score, general social-support deficit,
or binary risk indicator from this single statement.

### Source and measurement limitations

The source paper includes the statement “There are people I can count on in
this neighbourhood” with four agreement categories but supplies no scoring
rule or cutoff. In neighbourhood-social-cohesion research, this statement is
normally one of four items covering mutual help, dependable people, trust, and
neighbourhood closeness. Complete versions may sum or average the four items.

HEALIE contains only the dependable-people statement. It therefore cannot
validly reproduce the complete social-cohesion scale or its published scores.
The item also concerns the participant's neighbourhood specifically; it does
not assess support from family, friends, colleagues, online communities, or
people living elsewhere.

### Approved calculation and representation

```json
{
  "neighborhood_support_context": {
    "assessment_status": "assessed",
    "perceived_support": "somewhat_disagree"
  }
}
```

The preserved ordered categories are:

- `definitely_agree`;
- `somewhat_agree`;
- `somewhat_disagree`; and
- `definitely_disagree`.

No category is converted into a binary support-deficit flag. A missing required
response is `not_assessed`.

### Construct boundaries and relationship with Q17

Q17 measures frequency of contact with people the participant cares about and
feels close to. Q18 measures perceived availability of someone dependable in
the neighbourhood. Neither field fills, overwrites, or determines the other.

Disagreement with Q18 does not prove that the participant lacks practical,
informational, financial, healthcare-related, or emotional support. Agreement
does not prove that neighbours are willing or able to provide any particular
kind of assistance.

### Personalisation and Sørensen model role

Perceived local support might later relate to Access, Appraise, and Apply by
making local knowledge or practical assistance available. Q18 alone does not
establish consent to involve another person or the suitability of neighbour
support. No dimension weights or automatic adaptations are assigned now.

### Prohibited inferences

Q18 must not independently produce:

- `low_neighborhood_cohesion`;
- a general social-support deficit or social isolation result;
- loneliness, depression, vulnerability, or low health literacy;
- permission to disclose information to or involve neighbours;
- neighbourhood safety, trust, or collective efficacy; or
- a combined Q17/Q18 social-risk score.

### Deferred HEALIE decisions

- Whether a complete validated neighbourhood-social-cohesion measure is needed
  for a future research version.
- Whether local-resource adaptations should ever use this contextual response.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Joint interpretation with Q17, family context, transport, and mental-health
  indicators.

### References

1. Pariyo GW, et al. Standardizing social determinants of health data: a
   proposal for a comprehensive screening tool to address health equity—a
   systematic review. *Health Affairs Scholar.* 2024;2(12):qxae151.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11642620/
2. Quinn TD, et al. Associations between neighborhood social cohesion and
   health outcomes in the National Health Interview Survey. *Prev Chronic Dis.*
   2019. https://www.cdc.gov/pcd/issues/2019/19_0085.htm
3. Stella SY, et al. Racial/ethnic differences in associations between
   neighborhood social cohesion and health. *Prev Chronic Dis.* 2016.
   https://www.cdc.gov/pcd/issues/2016/16_0261.htm

## Indicator 15: PHQ-2 depression screening result

### Decision

Calculate and expose the validated PHQ-2 total and a non-diagnostic positive
screen using the source questionnaire's threshold of `>= 3`. Preserve explicit
declined and not-assessed states. Do not expose the two item-level responses in
the standard HEALIE indicator payload.

### Approved calculation and representation

Each of the two items is scored from 0 to 3:

```text
phq2_score = phq2_item1 + phq2_item2
depression_screen_positive = phq2_score >= 3
```

The valid score range is 0–6.

```json
{
  "depression_screening": {
    "assessment_status": "assessed",
    "instrument": "phq_2",
    "score": 4,
    "screen_positive": true,
    "follow_up_assessment_indicated": true
  }
}
```

A participant who declines receives `assessment_status: "declined"`, with
`score`, `screen_positive`, and `follow_up_assessment_indicated` set to `null`.
If participation is accepted but either item is absent or invalid, the status is
`not_assessed`; no partial score is calculated.

### Interpretation correction

The source paper says that a score of 3 or greater means major depressive
disorder is likely. HEALIE adopts the more accurate interpretation: `>= 3` is a
**positive depression screen indicating further assessment**, commonly with
the full PHQ-9 or a clinical interview. It is not a diagnosis.

Although evidence supports alternative two-stage workflows, including PHQ-2
`>= 2` followed by PHQ-9, HEALIE retains `>= 3` for fidelity to the current
standalone source measure. Changing the workflow later would require an
explicit protocol decision and validation.

### Safety and construct boundaries

- A positive result does not diagnose a depressive disorder.
- A negative result does not establish absence of depression.
- PHQ-2 does not ask about self-harm or suicidal thoughts and is not a suicide-
  risk screen.
- The result must not determine treatment or emergency action without an
  appropriate clinical protocol.
- A translated implementation should use validated wording and should not
  assume identical operating characteristics without evaluation.

### Personalisation and Sørensen model role

Depressive symptoms may influence attention, motivation, confidence, appraisal,
and capacity to act, making Appraise and Apply plausible later mappings. No
weights or automatic emotional adaptations are assigned now. Future supportive
adaptations must not manipulate, alarm, patronise, reduce clinical detail, or
withhold information.

### Prohibited inferences

Q19a must not independently produce:

- `has_depression` or a psychiatric diagnosis;
- suicide or self-harm risk status;
- severity categories beyond what PHQ-2 validates;
- incapacity to consent or make decisions;
- low health literacy; or
- automatic treatment, referral, or content restriction.

### Deferred HEALIE decisions

- The clinical or research follow-up pathway after a positive screen.
- Whether a full PHQ-9 is administered conditionally.
- Validation and licensing checks for each deployed language version.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Governance for emotionally adaptive communication and access controls for
  sensitive mental-health indicators.

### References

1. Kroenke K, Spitzer RL, Williams JBW. The Patient Health Questionnaire-2:
   validity of a two-item depression screener. *Med Care.*
   2003;41(11):1284-1292.
2. Levis B, et al. Accuracy of the PHQ-2 alone and in combination with the
   PHQ-9 for screening to detect major depression. *JAMA.*
   2020;323(22):2290-2300. https://pubmed.ncbi.nlm.nih.gov/32515813/
3. Pariyo GW, et al. Standardizing social determinants of health data: a
   proposal for a comprehensive screening tool to address health equity—a
   systematic review. *Health Affairs Scholar.* 2024;2(12):qxae151.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11642620/

## Indicator 16: HITS intimate-partner-violence screening result

### Decision

Calculate the HITS total and source-based positive-screen result, but expose it
only within a restricted safety-indicator object rather than the ordinary
HEALIE personalisation profile. Preserve the original item meaning while
keeping the instrument acronym in metadata rather than participant-facing text.
The HITS questions remain available regardless of the answer to the current-
partner item.

### Approved questionnaire behaviour

- Keep `Do you currently have a partner?` unchanged.
- Display `How often does your partner do the following?` without the HITS
  acronym; retain `hits` internally as the instrument identifier.
- Do not rephrase the item to mention a current or former partner.
- Remove the HITS matrix's dependency on a `yes` answer to current-partner
  status.
- Allow the participant to complete HITS after `yes`, `no`, or
  `prefer_not_answer`.
- Do not use marital status or current-partner status to infer, block, pre-fill,
  or score the HITS responses.

### Approved calculation and restricted representation

Each of four items is scored from 1 (`never`) to 5 (`frequently`):

```text
hits_score = hurt + insult + threaten + scream
ipv_screen_positive = hits_score >= 11
```

The valid total range is 4–20. The original study reported an optimal cut score
of 10.5; because valid totals are integers, `>= 11` implements that rule.

```json
{
  "restricted_safety_indicators": {
    "ipv_screening": {
      "assessment_status": "assessed",
      "instrument": "hits",
      "score": 13,
      "threshold": 11,
      "threshold_basis": "original_english_hits",
      "screen_positive": true,
      "support_follow_up_indicated": true
    }
  }
}
```

There is no `not_administered_no_current_partner` state. If the required HITS
matrix is incomplete or invalid, its status is `not_assessed` and no score is
calculated. The standard indicator payload does not include the four item-level
responses.

### Greek and European validation decision

No peer-reviewed Greek-language HITS validation or Greek-specific HITS cutoff
was identified in the review. There is also no scientifically transferable
“European threshold”; thresholds depend on the exact language version,
population, setting, and reference standard.

Greek versions of other IPV measures have been studied: WAST among postpartum
women and the Abuse Assessment Screen among pregnant women. Those findings do
not validate Greek HITS and are not automatically generalisable to all adults.
HEALIE therefore retains `>= 11` as a provisional source-based threshold and
labels its threshold basis explicitly. Local validation limitations belong in
scientific documentation rather than the runtime indicator payload.

### Safety and governance requirements

The indicator must not be available to general content-personalisation,
analytics, advertising, or ordinary profile consumers. Operational use requires
privacy-preserving presentation, controlled access, an appropriate support
pathway, and governance for handling a positive result. Screening without a
safe and realistic response pathway can create harm.

### Construct limitations

- A positive HITS result is a screen, not a diagnosis or legal finding.
- A negative result does not establish safety.
- HITS does not comprehensively assess sexual violence, coercive control,
  stalking, economic abuse, or immediate danger.
- Current-partner status is not used to interpret a completed score.
- A declined or absent answer is not a negative screen.

### Prohibited uses and inferences

Q19b must not independently:

- alter reading level, tone, clinical detail, treatment information, or general
  recommendations;
- be converted into a generic vulnerability or health-literacy score;
- trigger disclosure to a partner, family member, or unauthorised professional;
- establish immediate danger, criminal conduct, or capacity; or
- be combined with marital status to infer relationship history.

### Deferred HEALIE decisions

- Formal Greek forward/back translation, cultural adaptation, cognitive
  interviewing, psychometric evaluation, and ROC-based cutoff validation.
- The precise confidential support and escalation pathway.
- Safe-exit, notification, screen-history, and device-privacy requirements.
- Retention, deletion, encryption, and role-based access rules for restricted
  safety indicators.
- Whether a broader validated IPV measure is needed to cover omitted domains.

### References

1. Sherin KM, Sinacore JM, Li XQ, Zitter RE, Shakil A. HITS: a short domestic
   violence screening tool for use in a family practice setting. *Fam Med.*
   1998;30(7):508-512. https://pubmed.ncbi.nlm.nih.gov/9669164/
2. Vivilaki VG, et al. Identifying intimate partner violence during the
   postpartum period in a Greek sample. *Arch Womens Ment Health.* 2010.
   https://pubmed.ncbi.nlm.nih.gov/20306211/
3. Tzamalouka G, et al. Abuse Assessment Screen questionnaire: the Greek
   validation. 2011. https://pubmed.ncbi.nlm.nih.gov/21355465/
4. World Health Organization. *Responding to intimate partner violence and
   sexual violence against women: WHO clinical and policy guidelines.* 2013.
   https://www.who.int/publications/i/item/9789241548595

## Indicator 17: GAD-2 anxiety screening result

### Decision

Calculate and expose the GAD-2 total and a non-diagnostic positive screen using
the standard threshold of `>= 3`. Preserve explicit declined and not-assessed
states. Do not include item-level responses or local-validation metadata in the
standard runtime payload.

### Approved calculation and representation

Each of the two items is scored from 0 to 3:

```text
gad2_score = gad2_item1 + gad2_item2
anxiety_screen_positive = gad2_score >= 3
```

The valid score range is 0–6.

```json
{
  "anxiety_screening": {
    "assessment_status": "assessed",
    "instrument": "gad_2",
    "score": 4,
    "threshold": 3,
    "threshold_basis": "standard_gad_2",
    "screen_positive": true,
    "follow_up_assessment_indicated": true
  }
}
```

A participant who declines receives `assessment_status: "declined"`, with
`score`, `screen_positive`, and `follow_up_assessment_indicated` set to `null`.
If participation is accepted but either item is absent or invalid, the status is
`not_assessed`; no partial score is calculated.

### Evidence and local-language limitation

The conventional `>= 3` threshold is supported by the original primary-care
validation and diagnostic meta-analysis. European-language studies demonstrate
that optimal cutoffs can vary by language and population; Finnish primary-care
data supported 3, while Latvian and Russian versions tested in Latvia favoured
2. No general-adult Greek GAD-2 validation was identified.

HEALIE retains the standard threshold for source fidelity. Translation and
validation limitations are documented here and are not emitted as a runtime
`local_validation_status` field.

### Safety and construct boundaries

- A positive result indicates that further assessment may be appropriate; it
  does not diagnose generalized anxiety disorder or another anxiety disorder.
- A negative result does not establish absence of anxiety.
- GAD-2 does not assess immediate danger, capacity, intelligence, or health
  literacy.
- It must not independently determine treatment or restrict information.

### Personalisation and Sørensen model role

Anxiety may influence risk interpretation, worry, confidence, attention, and
decision-making, making Appraise and Apply plausible later mappings. No weights
or automatic emotional adaptations are assigned now.

### Prohibited inferences

Q19c must not independently produce:

- `has_anxiety_disorder` or a psychiatric diagnosis;
- incapacity, low intelligence, or low health literacy;
- a suicide or immediate-safety result;
- a treatment recommendation; or
- automatic simplification, omission, or alarming reassurance.

### Deferred HEALIE decisions

- The follow-up pathway after a positive screen.
- Whether the full GAD-7 is administered conditionally.
- Greek translation and population-specific validation.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Governance for emotionally adaptive communication and access to sensitive
  mental-health indicators.

### References

1. Kroenke K, Spitzer RL, Williams JBW, Monahan PO, Löwe B. Anxiety disorders
   in primary care: prevalence, impairment, comorbidity, and detection. *Ann
   Intern Med.* 2007;146(5):317-325.
2. Plummer F, Manea L, Trepel D, McMillan D. Screening for anxiety disorders
   with the GAD-7 and GAD-2: a systematic review and diagnostic meta-analysis.
   *Gen Hosp Psychiatry.* 2016;39:24-31.
3. Vrublevska J, et al. Validation of the GAD-7 and GAD-2 in primary care in
   Latvia. *Front Psychiatry.* 2022;13:972628.
   https://doi.org/10.3389/fpsyt.2022.972628

## Indicator 18: self-reported cognitive-function context

### Decision

Retain Q19d as a HEALIE-specific contextual self-report and export its ordered
category. Do not score it or interpret it as a validated cognitive-impairment,
subjective-cognitive-decline, mild-cognitive-impairment, or dementia screen.

### Source and measurement limitations

Q19d is not part of the source paper's proposed questionnaire, and its exact
wording and three response levels were not identified as a validated cognitive
screen. It combines perceived memory/thinking difficulty with effects on daily
life in a single short question.

Established subjective-cognitive-decline surveillance approaches commonly ask
whether confusion or memory loss is becoming more frequent or worsening and
then assess effects on daily activities separately. Q19d does not reproduce a
complete validated instrument and must not use its thresholds or labels.

### Approved representation

```json
{
  "cognitive_function_context": {
    "assessment_status": "assessed",
    "self_reported_daily_life_impact": "mild_or_sometimes"
  }
}
```

The exported categories are:

- `none_reported`;
- `mild_or_sometimes`; and
- `frequent_or_significant`.

The participant's `prefer_not_to_say` response produces
`assessment_status: "declined"` and a `null` category. A missing required
response is `not_assessed`. No redundant boolean or score is added.

### Personalisation and Sørensen model role

The response may support optional interface adaptations that reduce working-
memory burden, such as shorter steps, consistent terminology, summaries,
repetition, reminders, save-and-return, and clear navigation. These adaptations
should be offered or applied conservatively without removing information.

Understand and Apply are plausible later mappings, but no weights are assigned
now.

### Construct limitations and prohibited inferences

Memory or thinking concerns may reflect many temporary or persistent factors,
including stress, depression, anxiety, poor sleep, medication effects, illness,
or cognitive disorders. Q19d does not identify a cause.

It must not independently produce:

- cognitive impairment, mild cognitive impairment, or dementia;
- an MMSE or other objective-test estimate;
- incapacity to consent or make decisions;
- low intelligence or low health literacy;
- an age-related assumption; or
- automatic simplification, omission, or restriction of content.

### Deferred HEALIE decisions

- Whether a validated subjective-cognitive-decline or cognitive screening tool
  is needed for a research or clinical version.
- Which interface adaptations are offered for each response category.
- Relationships and weights for Access, Understand, Appraise, and Apply.
- Interaction with depression, anxiety, disability, age, and any clinician-
  administered cognitive assessment.

### Explicit exclusion: optional MMSE total (former Q19e)

The optional clinician-entered MMSE total is removed completely from the
questionnaire and indicator export.

Rationale:

- it does not appear in the original questionnaire that this adaptation aims
  to preserve;
- it would mix a participant-facing determinants screener with a separately
  administered clinical cognitive instrument;
- a total score cannot be interpreted responsibly through one universal
  cutoff without considering factors such as age, education, language, and
  assessment context; and
- reproducing or administering MMSE content would introduce separate licensing
  and governance requirements.

HEALIE will therefore receive no MMSE field, placeholder, `not_available`
status, derived impairment classification, or MMSE-based personalisation rule.
The retained Q19d response remains self-reported cognitive-function context and
must not be treated as a substitute for MMSE.

### References

1. Centers for Disease Control and Prevention. Behavioral Risk Factor
   Surveillance System Cognitive Decline optional module.
2. Jessen F, et al. A conceptual framework for research on subjective cognitive
   decline in preclinical Alzheimer's disease. *Alzheimers Dement.*
   2014;10(6):844-852.

## Indicator 19: Physical activity

### Decision

Retain the original two physical-activity questions and the original source
calculation. The participant reports:

- the average number of days per week on which they performed moderate exercise
  during the previous 30 days, excluding activity performed for work; and
- the usual number of minutes performed on one of those days.

Weekly activity is calculated as:

```text
weekly_minutes_activity = days_per_week × minutes_per_active_day
```

The source questionnaire defines a physical-activity need using the following
age-dependent thresholds:

- ages 16–17 in the HEALIE population: fewer than 420 minutes per week; and
- ages 18 or older: fewer than 150 minutes per week.

If age is unavailable or declined, weekly minutes may still be calculated, but
`physical_activity_need` is `not_assessed` because no age-dependent threshold
can be selected safely.

### Approved export

```json
{
  "weekly_minutes_activity": 120,
  "physical_activity_need": true
}
```

The need field is `false` when the relevant threshold is met and
`not_assessed` when the age threshold cannot be selected.

### Interpretation and limitations

This reproduces the calculation specified by the source questionnaire. It is a
screening indicator, not a diagnosis or a complete assessment of physical
activity. The questions exclude occupational activity and do not separately
measure vigorous activity, muscle strengthening, balance activity, sedentary
behaviour, or every form of transport and household activity addressed by WHO
guidance. The highest answer category, `150 or more`, may also make the
calculated weekly total a conservative minimum rather than an exact value.

These qualifications remain in the scientific documentation and do not add
extra fields to the runtime export.

### HEALIE role and prohibited inferences

The result is behavioural context that may later help select relevant examples
or supportive information. It must not independently be interpreted as low
motivation, poor adherence, low health literacy, disability, or a clinical
condition. No Sørensen-dimension relationship or weight is assigned now.

### References

1. *Standardizing social determinants of health data: a proposal for a
   comprehensive screening tool to address health equity: a systematic
   review.* Health Affairs Scholar. 2024.
2. World Health Organization. *WHO guidelines on physical activity and
   sedentary behaviour.* 2020.
3. LOINC 89555-7 and 68516-4, Accountable Health Communities HRSN supplemental
   physical-activity questions.

## Indicator 20: Health-harming legal needs and access to support

### Decision

Retain the separately identified, I-HELP-informed legal-needs module. It is an
addition to, not an original component of, the source SDoH questionnaire. The
module records:

- whether the participant reports a problem for which legal information,
  advice, or support might have been useful;
- the coded problem domain or domains; and
- whether the participant obtained the support they needed.

No numerical score, severity level, or cumulative domain count is calculated.
This follows common medical-legal-partnership practice, in which positive needs
are recorded by domain and used to support referral rather than combined into a
universal scale.

### Approved export

```json
{
  "legal_need_domains": [
    "housing_utilities"
  ],
  "legal_support_access": "cost_or_access_barrier",
  "potential_unmet_legal_need": true
}
```

The participant's free-text description of an `other` domain is not exported to
HEALIE. Only the coded `other` category is retained.

### Derivation of potential unmet need

`potential_unmet_legal_need` is `true` when the participant reports:

- some support, but not enough;
- trying to obtain support but receiving none;
- not knowing where to seek support; or
- a cost or other access barrier.

It is `false` when all required support was received or when no relevant legal
problem was reported. Choosing not to seek support is not automatically
classified as an access failure.

It is `null` when the participant is unsure, declines the relevant question, or
provides insufficient information. These states must not be converted to
`false`.

### Interpretation and HEALIE role

The result indicates a potential unresolved health-harming legal need, not a
legal diagnosis or determination that a legal remedy exists. Domains and access
barriers may later support appropriate signposting or contextual information.
They must not independently be used to infer vulnerability, immigration status,
poverty, low health literacy, or willingness to seek help.

Legal-support access may plausibly relate to the Access and Apply dimensions of
the Sørensen model, but no relationship weight or automatic personalisation rule
is assigned now.

### References and comparison

1. National Center for Medical-Legal Partnership. *Screening Tool for MLP Legal
   Needs in Health Care Settings* (I-HELP framework).
2. Trott J, Regenstein M. *Screening for Health-Harming Legal Needs.* Medical
   Legal Partnership Measurement Series.
3. OECD and Open Society Foundations. *Legal Needs Surveys and Access to
   Justice.* 2019.
4. *How legal problems are conceptualized and measured in healthcare settings:
   a systematic review.* Health & Justice. 2023.

## Indicator 21: Digital access and inclusion barriers

### Decision

Retain the six project-authored Digital Access and Inclusion items as distinct
Digital Determinants of Health indicators. Do not combine them into a global
digital-exclusion, digital-literacy, SDoH, or health-literacy score.

The export contains six nullable Boolean barriers:

- `device_access_barrier`;
- `connectivity_barrier`;
- `affordability_barrier`;
- `accessibility_barrier`;
- `support_barrier`; and
- `privacy_trust_barrier`.

For frequency items, Sometimes and Never indicate a barrier; Always and Often
do not. For yes/no barrier items, Yes indicates a barrier and No does not.
Prefer not to answer, Not sure, Not used, missing information, or an otherwise
non-interpretable response produces `null`, never `false`. “I do not need
assistance” produces `support_barrier: false` because it is an explicit response
that assistance is not required.

Home internet (Q11) is not interpreted alone. It is combined with the personal
connectivity response to describe an `internet_access_level`, distinguishing
reliable home-supported access, reliable mobile/non-home access, intermittent
access, access that is nominally present but unusable for digital health, and no
usable access. This avoids treating absence of fixed home internet as equivalent
to complete digital exclusion.

These indicators describe structural and practical access conditions. They do
not measure digital or eHealth literacy. eHEALS remains deferred to a separate
HEALIE component.

## Versioned HEALIE integration contract

### Decision

The SD-DOH component exports a data-minimised, versioned contract rather than a
verbatim questionnaire record. Version 1.0 is organized into four information
tiers:

1. `context`: approved descriptive information that may shape accessibility,
   relevance or service linkage;
2. `needs`: derived nullable needs and barriers;
3. `screening_results`: non-safety screening results without raw item answers;
4. `restricted_safety_indicators`: HITS/IPV results requiring separate access
   control.

The retained exceptions requested for HEALIE are household-income band or its
assessment status; gender, ethnic group, European region and ancestry; postal
code; marital status; usual travel mode; and the combination of household home
internet with personal connectivity. Ancestry is the only approved retained
free-text response. Other free-text specifications are not exported.

Postal code is retained solely as a controlled geographic-linkage input for
environmental and socioeconomic enrichment. It should not be copied directly
into general-purpose language-model prompts, displayed unnecessarily, or used
as a proxy for an individual's characteristics without a documented linkage
method and governance controls.

The payload deliberately omits:

- raw PHQ-2, GAD-2 and HITS item answers;
- MMSE data or an MMSE-derived result;
- scoring thresholds and threshold provenance;
- free-text Other specifications other than ancestry;
- a combined SDoH, DDoH or health-literacy score; and
- personalisation weights or automated impact estimates.

Uncertain, declined, not-applicable and not-assessed states remain explicit or
produce `null` indicators. They are not silently encoded as absence of need.
The machine contract is defined in `healie_indicator_export_schema_v1.json` and
is validated by the API before a response is returned.

### Assessment-export identity and provenance

Each successful final full-assessment validation produces a new
backend-generated UUIDv4 `assessment_id` and a UTC `generated_at` timestamp.
Section-level navigation validation does not create or return an indicator
export. The identifier belongs to the completed export event only. It is random,
is not calculated from questionnaire answers, and must not be interpreted as a
participant, patient, account or longitudinal subject identifier.

HEALIE may use `assessment_id` for request tracing, deduplication and linking
downstream processing results to the exact indicator export. If longitudinal
linkage is later required, the wider HEALIE system must provide a distinct,
governed pseudonymous `subject_id`. The SD-DOH component must not derive that
identifier from postal code, demographics, device data or any other answer.

### Deferred work

Research-mode storage of verbatim answers, indicator weights, links to the four
Sørensen health-literacy dimensions, and outcome-based validation remain in the
research/validation backlog. They are not part of the current operational
HEALIE export.

## Participant-facing language convention

### Decision

Participant-facing questions consistently address the person completing the
assessment in the second person (`you`/`your`). Functional-difficulty rows that
previously switched to census-style third-person wording (`this person`) were
normalized without changing their measured domains. Age qualifiers attached to
those source rows were removed because this assessment begins at age 16.

Questions intentionally assessing shared circumstances retain their household
scope, using the consistent phrase `you or anyone in your household`. The
neighbourhood-support statement was changed from first person to second person
for interface consistency. These wording adaptations must be included in later
cognitive interviewing and translation/back-translation review.

PHQ-2, GAD-2, and HITS names remain in question identifiers, scoring metadata,
indicator exports, documentation, and the research audit trail, but their
acronyms are not shown within the participant-facing prompts. Removing the
labels does not change the item text, response scales, scoring, or thresholds.
