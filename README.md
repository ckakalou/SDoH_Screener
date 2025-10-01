

# SDoH Screener Demo (Python + Streamlit)

This is a quick demo app that renders the Social Determinants of Health (SDoH) screener from a JSON config,
validates responses with a JSON Schema, and computes key flags and scores (PHQ-2, HITS, Physical Activity).

## 1) Set up (macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Run the app
```bash
streamlit run app.py
```
The browser will open automatically (usually at http://localhost:8501).

## 3) What this demo does
- Renders form sections from `sdoh_screener.json`
- Applies basic skip logic (employment sub-questions, unmet-needs follow-ups)
- Validates the submitted payload with `sdoh_screener_response_schema.json`
- Computes and displays:
  - PHQ-2 total and screen result
  - HITS total and screen result (Spanish cutoff toggle)
  - Physical-activity weekly minutes and need flag (based on age)
  - Other flags: housing instability, transportation need, food insecurity, medical cost barrier
- Lets you download the **response payload** and **evaluation results** as JSON

## 4) Files
- `app.py` – Streamlit app
- `sdoh_screener.json` – Form configuration
- `sdoh_screener_response_schema.json` – JSON Schema for responses
- `requirements.txt` – Dependencies

## 5) Notes
- This is a demo; production apps should persist responses and add authentication/consent.
- You can customize the UI easily by editing `app.py`.
