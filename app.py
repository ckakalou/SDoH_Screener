import json
from pathlib import Path
import streamlit as st
from jsonschema import Draft202012Validator
import pandas as pd

st.set_page_config(page_title="SDoH Screener Demo", layout="wide")

st.set_page_config(
    page_title="SDoH Screener Demo",
    page_icon="sdoh_favicon.png",
    layout="wide"
)

# Custom CSS to change selection color and widget focus styles
st.markdown(
    """
    <style>
    ::selection {
        background: #98FF98; /* mint green */
        color: black;
    }
    /* Change focus/selection border color to mint green */
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stMultiSelect > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #98FF98 !important;
        box-shadow: 0 0 0 1px #98FF98 !important;
    }
    .stCheckbox input:checked {
        accent-color: #98FF98 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

CFG_PATH = Path(__file__).parent / "sdoh_screener.json"
SCHEMA_PATH = Path(__file__).parent / "sdoh_screener_response_schema.json"

@st.cache_data
def load_cfg():
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ---- utils: enum widgets + normalization ----
def select_enum(label, enum_map, *, key=None, default_label=None):
    """Render a selectbox with human labels but return the canonical enum value."""
    labels = list(enum_map.keys())
    index = labels.index(default_label) if default_label in labels else None
    chosen_label = st.selectbox(label, labels, index=index, key=key)
    return enum_map[chosen_label] if chosen_label else None

def normalize_values(responses):
    """Coerce any stray UI labels to canonical enum values and fix common type issues."""
    worry_label_to_value = {
        "Very worried": "very_worried",
        "Moderately worried": "moderately_worried",
        "Not too worried": "not_too_worried",
        "Not worried at all": "not_worried",
    }
    for k in ("q16c_worry_housing_repeat", "q16d_worry_bills"):
        v = responses.get(k)
        if v in worry_label_to_value:
            responses[k] = worry_label_to_value[v]
    # q20a_pa_days is a string enum ("0".."7") in the config; ensure string
    if "q20a_pa_days" in responses and isinstance(responses["q20a_pa_days"], int):
        responses["q20a_pa_days"] = str(responses["q20a_pa_days"])
    return responses

cfg = load_cfg()
schema = load_schema()
questions = cfg["screener"]["questions"]

st.title("SDoH Screener Demo")
st.caption("Renders from JSON config, validates with JSON Schema, and computes flags/scores.")

# Sidebar branding
st.sidebar.image("sdoh_favicon.png", width=64)
st.sidebar.markdown("### About this Screener")
st.sidebar.write(
    "This Social Determinants of Health (SDoH) screener helps identify "
    "social and economic factors that can impact health. Your responses "
    "will highlight areas such as housing, food, transportation, and access "
    "to care, which can be used to provide more personalized support."
)
# Sidebar context
st.sidebar.header("Context")
age_years = st.sidebar.number_input("Age (years)", min_value=0, max_value=120, value=30, step=1)
spanish_version = st.sidebar.checkbox("Spanish IPV cutoff (5.5)", value=False)

st.sidebar.markdown("### Health Literacy Context (Sørensen et al.)")
preferred_lang = st.sidebar.selectbox(
    "Preferred language for health information",
    ["Greek", "English", "Spanish", "Other"]
)
conf_forms = st.sidebar.radio(
    "Confidence filling out medical forms by yourself",
    ["Not at all", "A little", "Somewhat", "Quite a bit", "Extremely"]
)
digital_comfort = st.sidebar.radio(
    "Comfort using digital tools (apps, internet) for health information",
    ["Low", "Medium", "High"]
)
support = st.sidebar.checkbox("I have someone who helps me understand health information")

st.sidebar.markdown("### IPV Cutoff Selection")
st.sidebar.write(
    "The HITS screening tool uses different validated cutoffs depending on language: "
    "- **English:** ≥10.5\n"
    "- **Spanish:** ≥5.5\n\n"
    "Select Spanish cutoff if administering to Spanish-speaking participants, based on "
    "validation studies showing different sensitivity/specificity thresholds."
)
spanish_version = st.sidebar.checkbox("Apply Spanish cutoff (5.5 instead of 10.5)", value=False)


# Helper for visible_if
def check_visible_if(visible_if, answers):
    if not visible_if:
        return True
    def eval_condition(cond):
        qid = cond.get("question")
        op = cond.get("operator", "=")
        val = cond.get("value")
        ans = answers.get(qid)
        if op == "=":  return ans == val
        if op == "!=": return ans != val
        return True
    if "any" in visible_if: return any(eval_condition(c) for c in visible_if["any"])
    if "all" in visible_if: return all(eval_condition(c) for c in visible_if["all"])
    return True

# Render widgets
st.subheader("Screener")
with st.form("sdoh_form"):
    responses = {}
    for q in questions:
        qid = q["id"]
        qtype = q["type"]
        label = q["text"]
        visible_if = q.get("visible_if")
        if not check_visible_if(visible_if, responses):
            continue

        if qtype == "single-select":
            opts = q["options"]
            labels = [opt["label"] if isinstance(opt, dict) else str(opt) for opt in opts]
            values = [opt["value"] if isinstance(opt, dict) else opt for opt in opts]
            sel_label = st.selectbox(label, labels, index=None, placeholder="Select an option", key=qid)
            if sel_label is not None:
                responses[qid] = values[labels.index(sel_label)]

        elif qtype == "multi-select":
            opts = q["options"]
            labels = [opt["label"] if isinstance(opt, dict) else str(opt) for opt in opts]
            values = [opt["value"] if isinstance(opt, dict) else opt for opt in opts]
            sel_labels = st.multiselect(label, labels, key=qid)
            responses[qid] = [values[labels.index(lab)] for lab in sel_labels]

        elif qtype == "boolean":
            responses[qid] = st.checkbox(label, value=False, key=qid)

        elif qtype == "integer":
            minv = q.get("min", 0)
            responses[qid] = int(st.number_input(label, min_value=minv, value=minv, step=1, key=qid))

        elif qtype == "currency":
            responses[qid] = float(st.number_input(label, min_value=0.0, value=0.0, step=1.0, key=qid))

        elif qtype == "text":
            responses[qid] = st.text_input(label, value="", key=qid)

        elif qtype == "group":
            items = q["items"]
            buf = {}
            st.markdown(f"**{label}**")
            for item in items:
                itype = item["type"]
                iid = item["id"]
                itext = item["text"]
                if itype == "currency":
                    buf[iid] = float(st.number_input(itext, min_value=0.0, value=0.0, step=1.0, key=iid))
                elif itype == "boolean":
                    buf[iid] = st.checkbox(itext, value=False, key=iid)
                elif itype == "text":
                    buf[iid] = st.text_input(itext, value="", key=iid)
                else:
                    buf[iid] = st.text_input(itext, value="", key=iid)
            responses[qid] = buf

        elif qtype == "checklist":
            items = q["items"]
            buf = {}
            st.markdown(f"**{label}**")
            for item in items:
                iid = item["id"]
                itext = item["label"]
                itype = item.get("type", "boolean")
                if itype == "boolean":
                    buf[iid] = st.checkbox(itext, value=False, key=iid)
                elif itype == "text":
                    buf[iid] = st.text_input(itext, value="", key=iid)
            responses[qid] = buf

            # Follow-ups for unmet needs
            if qid == "q16_unmet_needs":
                needs_true = any(buf.get(iid) for iid in ["q16_food","q16_healthy_food","q16_healthcare","q16_phone"])
                if needs_true:
                    st.markdown("**Follow-up Questions**")
                    responses["q16a_medical_bills"] = st.checkbox(
                        "During the past 12 months, problems paying or unable to pay any medical bills?",
                        value=False
                    )
                    responses["q16b_delayed_care_cost"] = st.checkbox(
                        "During the past 12 months, was medical care delayed because of worry about the cost?",
                        value=False
                    )
                    worry_map = {
                        "Very worried": "very_worried",
                        "Moderately worried": "moderately_worried",
                        "Not too worried": "not_too_worried",
                        "Not worried at all": "not_worried",
                    }
                    responses["q16c_worry_housing_repeat"] = select_enum(
                        "How worried are you right now about not being able to pay your rent, mortgage, or other housing costs?",
                        worry_map, default_label="Moderately worried", key="q16c_worry_housing_repeat"
                    )
                    responses["q16d_worry_bills"] = select_enum(
                        "How worried are you right now about not being able to pay your normal monthly bills?",
                        worry_map, default_label="Moderately worried", key="q16d_worry_bills"
                    )

        elif qtype == "matrix":
            scale = q["scale"]
            rows = q["rows"]
            labels = [s["label"] for s in scale]
            values = [s["value"] for s in scale]
            buf = {}
            st.markdown(f"**{label}**")
            for row in rows:
                choice = st.radio(row["label"], labels, horizontal=True, index=0, key=row["id"])
                buf[row["id"]] = values[labels.index(choice)]
            responses[qid] = buf

    submitted = st.form_submit_button("Submit and Validate")

if submitted:
    st.subheader("Validation")

    # Normalize before schema validation
    responses = normalize_values(responses)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(responses), key=lambda e: list(e.path))
    if errors:
        st.error("Validation failed. See errors below:")
        for e in errors:
            st.write(f"• At {list(e.path)}: {e.message}")
    else:
        st.success("Schema validation passed ✅")

    # --- Compute scores & flags ---
    st.subheader("Computed Scores & Flags")

    phq2 = responses.get("q19a_phq2") or {}
    phq2_score = sum(int(phq2.get(k,0)) for k in ["phq2_item1","phq2_item2"])
    phq2_positive = phq2_score >= 3

    hits = responses.get("q19b_ipv_hits") or {}
    hits_score = sum(float(hits.get(k,0)) for k in ["hits_hurt","hits_insult","hits_threaten","hits_scream"])
    hits_cutoff = 5.5 if spanish_version else 10.5
    hits_positive = hits_score >= hits_cutoff

    # Physical Activity
    try:
        days = int(responses.get("q20a_pa_days") or 0)
    except Exception:
        days = 0
    try:
        minutes = int(responses.get("q20b_pa_minutes") or 0)
    except Exception:
        minutes = 0
    weekly_minutes = days * minutes
    if 6 <= age_years <= 17:
        pa_need = weekly_minutes < (60*7)
    elif age_years >= 18:
        pa_need = weekly_minutes < 150
    else:
        pa_need = False

    # Flags
    housing_instability = (
        responses.get("q6a_housing_situation") in ["worried_losing","no_housing"]
        or responses.get("q6d_difficult_to_pay_housing") is True
    )
    transport_need = responses.get("q15b_transport_barrier") is True
    unmet = (responses.get("q16_unmet_needs") or {})
    food_insecurity = bool(unmet.get("q16_food") or unmet.get("q16_healthy_food"))
    medical_cost_barrier = bool(responses.get("q16a_medical_bills") or responses.get("q16b_delayed_care_cost"))

    results = {
        "phq2_score": phq2_score,
        "depression_screen_positive": phq2_positive,
        "hits_score": hits_score,
        "ipv_screen_positive": hits_positive,
        "hits_cutoff": hits_cutoff,
        "weekly_minutes_activity": weekly_minutes,
        "physical_activity_need": pa_need,
        "housing_instability": housing_instability,
        "transportation_need": transport_need,
        "food_insecurity": food_insecurity,
        "medical_cost_barrier": medical_cost_barrier,
        "age_years": age_years,
        "spanish_version": spanish_version
    }

    st.write(pd.DataFrame([results]).T.rename(columns={0:"value"}))
    # --- IPV safety flow (shows only when screen is positive) ---
    if results.get("ipv_screen_positive"):
        st.error("Safety notice: Your answers suggest possible risk related to intimate partner violence.")
        st.markdown(
            """
    If you feel unsafe **right now**, consider these options:

    - **EU emergency number:** **112** (free, 24/7 across the EU).
    - **Greece (local):**  
      • **Police:** **100** (you can also SMS your address, name, and “I am in danger”).  
      • **Women SOS hotline:** **15900** — psychosocial support, legal counselling, and access to shelters (`sos15900@isotita.gr`).

    If you are outside Greece, contact your **local emergency number** or your country’s **domestic violence hotline**.

    You are not alone. Support is available. Share only what you’re comfortable sharing, and use a safe device if possible.
            """
        )
    st.markdown("### Interpretation for Researchers")
    st.markdown(
        """
**Computed indicators (post-validation):**

- **`phq2_score`**: Sum of the two PHQ-2 items (0–6). **≥ 3** indicates a positive depression screen.
- **`depression_screen_positive`**: Boolean flag set to `true` when `phq2_score ≥ 3`.
- **`hits_score`**: Sum of HITS items (4–20 typical; Spanish form uses 1–5 per item). Risk threshold depends on language.
- **`ipv_screen_positive`**: `true` if `hits_score ≥ hits_cutoff`.
- **`hits_cutoff`**: Language-specific cutoff (default **10.5**; if Spanish version selected, **5.5**).
- **`weekly_minutes_activity`**: `q20a_pa_days × q20b_pa_minutes`. Benchmarked vs guidelines.
- **`physical_activity_need`**: `true` if below guideline (Adults **<150 min/week**; ages 6–17 **<420 min/week**).
- **`housing_instability`**: `true` if current housing is unstable or paying for housing is difficult.
- **`transportation_need`**: `true` if transportation barriers are reported.
- **`food_insecurity`**: `true` if food-related unmet needs are checked.
- **`medical_cost_barrier`**: `true` if problems paying medical bills or delayed care due to cost.
- **`age_years`**: Age used to select the appropriate physical activity benchmark.
- **`spanish_version`**: Whether the Spanish IPV cutoff (**5.5**) is applied.

**Health literacy note:** Presenting these results in plain language (e.g., what “positive screen” means and next steps) supports **health literacy**, enabling participants to understand findings and act on social and behavioral determinants alongside clinical care.
"""
    )
    st.subheader("Submitted Payload")
    st.json(responses)
    st.download_button("Download responses.json", data=json.dumps(responses, indent=2), file_name="responses.json")
    st.download_button("Download results.json", data=json.dumps(results, indent=2), file_name="results.json")