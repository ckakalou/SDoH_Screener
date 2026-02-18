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
- Mental health: retained **PHQ-2** and added **GAD-2** (anxiety) as an additional brief screener.
- Cognition: added an optional **self-report cognition** item and an optional field for a clinician-entered **MMSE total score** (0–30) without embedding MMSE item text.

## Files
- `sdoh_screener_eu_gr_v2.json` — screener definition (questions, types, options)
- `sdoh_screener_response_schema_eu_gr_v2.json` — JSON Schema for validating `responses.json`
- `app_eu_gr_v2.py` — Streamlit app (renders screener + computes scores/flags)

## Derived indicators computed in the app
From submitted responses, the app computes:

- **PHQ-2 score** (0–6) and `depression_screen_positive` (PHQ-2 ≥ 3)
- **GAD-2 score** (0–6) and `anxiety_screen_positive` (GAD-2 ≥ 3)
- **HITS score** (4–20) and `ipv_screen_positive` (cutoff configurable; default 10.5, optional 5.5)
- **Weekly physical activity minutes** and `physical_activity_need` (age-aware threshold)
- Needs/flags:
  - `housing_instability`
  - `transportation_need`
  - `food_insecurity`
  - `medical_cost_barrier`
- Context variables:
  - `cognition_selfreport`
  - `mmse_total` (optional)

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

## Notes on safety & IPV screening
If IPV screen is positive, the UI should avoid displaying sensitive advice in a way that could increase risk.
For production use, implement a safety protocol appropriate to your local clinical context.

Generated on 2026-02-04.

Digital device access need is flagged when the respondent reports having no device access or only intermittent access (“sometimes”).
