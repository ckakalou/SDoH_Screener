# SDoH Screener Demo (Python + Streamlit) — EU/GR v2

This demo renders an **EU/Greek-adapted** Social Determinants of Health (SDoH) screener from a JSON config,
validates responses with a JSON Schema, and computes key derived indicators.

**Expert review panel (content/cultural validation):**
- Konstantina Stavrogianni (KS), Psychologist, MSc Public Health
- Antonis Bozas (AB), Medical Psychologist, PhD (medical/health sciences)
- Mara Gkioka (MG), Neuropsychologist, PhD

## What changed vs. the original (US-oriented) draft
Key adaptations based on KS/AB/MG review:
- Demographics: “Race” reframed as **ethnic group**; added **European region** question.
- Income: switched from exact amount to **income brackets** (euros) for acceptability.
- Education and employment: options updated to better fit **European** contexts.
- Housing: removed **mobile home** option.
- Health coverage: replaced US-specific insurance checklist with **public/private coverage** categories.
- Mobility/transport: commute options adapted to common EU modes.
- Depression and anxiety screening is deferred to separate HEALIE instruments.
- HITS/IPV screening is outside the current prototype scope because it lacks the required safeguarding and linkage-to-care pathway.
- Cognition is retained as self-reported context only; MMSE is excluded.

## Files
- `sdoh_screener_eu_gr_v2.json` — screener definition (questions, types, options)
- `sdoh_screener_response_schema_eu_gr_v2.json` — JSON Schema for validating `responses.json`
- `app_eu_gr_v2.py` — Streamlit app (renders screener + computes scores/flags)

## Derived indicators computed in the app
From submitted responses, the app computes:

- **Weekly physical activity minutes** and `physical_activity_need` (age-aware threshold)
- Needs/flags:
  - `housing_instability`
  - `transportation_need`
  - `food_insecurity`
  - `medical_cost_barrier`
- Context variables:
  - `cognition_selfreport`

## Run locally (macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app_eu_gr_v2.py
```

## Outputs
After submission the app provides:
- `responses.json` — verbatim answers
- `results.json` — computed scores and flags (derived indicators)

## Scope note
The active React/FastAPI implementation is authoritative. This Streamlit app is
retained as a legacy prototype and must not be used as a clinical assessment.

Generated on 2026-02-04.

Digital device access need is flagged when the respondent reports having no device access or only intermittent access (“sometimes”).
