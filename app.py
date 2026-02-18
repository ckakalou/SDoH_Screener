import json
from pathlib import Path

import pandas as pd
import streamlit as st
from jsonschema import Draft202012Validator

CFG_PATH = Path(__file__).parent / "sdoh_screener.json"
SCHEMA_PATH = Path(__file__).parent / "sdoh_screener_response_schema.json"

st.set_page_config(
    page_title="SDoH Screener",
    page_icon="sdoh_favicon.png",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --mint: #9be7c4;
        --mint-dark: #49b38a;
        --panel: #f7fbf9;
    }

    .hero {
        background: linear-gradient(135deg, #f5fffa 0%, #eefaf5 100%);
        border: 1px solid #d8f0e4;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0 0 0.25rem 0;
        color: #1f4b3f;
    }

    .hero p {
        margin: 0;
        color: #2d5f50;
    }

    .panel {
        background: var(--panel);
        border: 1px solid #e2efe8;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.4rem 0 1rem 0;
    }

    ::selection {
        background: var(--mint);
        color: black;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px;
        border: 1px solid var(--mint-dark);
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stMultiSelect > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--mint-dark) !important;
        box-shadow: 0 0 0 1px var(--mint-dark) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_cfg():
    with CFG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_schema():
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def select_enum(label, enum_map, *, key=None, default_label=None):
    labels = list(enum_map.keys())
    index = labels.index(default_label) if default_label in labels else None
    chosen_label = st.selectbox(label, labels, index=index, key=key)
    return enum_map[chosen_label] if chosen_label else None


def normalize_values(responses):
    worry_label_to_value = {
        "Very worried": "very_worried",
        "Moderately worried": "moderately_worried",
        "Not too worried": "not_too_worried",
        "Not worried at all": "not_worried",
    }
    for key in ("q16c_worry_housing_repeat", "q16d_worry_bills"):
        value = responses.get(key)
        if value in worry_label_to_value:
            responses[key] = worry_label_to_value[value]

    if "q20a_pa_days" in responses and isinstance(responses["q20a_pa_days"], int):
        responses["q20a_pa_days"] = str(responses["q20a_pa_days"])
    return responses


def check_visible_if(visible_if, answers):
    if not visible_if:
        return True

    def eval_condition(cond):
        qid = cond.get("question")
        op = cond.get("operator", "=")
        val = cond.get("value")
        ans = answers.get(qid)
        if op == "=":
            return ans == val
        if op == "!=":
            return ans != val
        return True

    if "any" in visible_if:
        return any(eval_condition(c) for c in visible_if["any"])
    if "all" in visible_if:
        return all(eval_condition(c) for c in visible_if["all"])
    return True


def render_sidebar():
    st.sidebar.image("sdoh_favicon.png", width=56)
    st.sidebar.markdown("### About")
    st.sidebar.write(
        "This screener highlights social, economic, and behavioral factors that may affect health outcomes."
    )

    st.sidebar.markdown("### Context Inputs")
    age_years = st.sidebar.number_input("Age (years)", min_value=0, max_value=120, value=30, step=1)

    st.sidebar.markdown("### Health Literacy Context")
    st.sidebar.selectbox(
        "Preferred language for health information",
        ["Greek", "English", "Spanish", "Other"],
    )
    st.sidebar.radio(
        "Confidence filling out medical forms by yourself",
        ["Not at all", "A little", "Somewhat", "Quite a bit", "Extremely"],
    )
    st.sidebar.radio(
        "Comfort using digital tools for health information",
        ["Low", "Medium", "High"],
    )
    st.sidebar.checkbox("I have someone who helps me understand health information")

    st.sidebar.markdown("### IPV Cutoff")
    st.sidebar.write("Use Spanish cutoff when the validated Spanish version of HITS is administered.")
    spanish_version = st.sidebar.checkbox("Apply Spanish cutoff (5.5 instead of 10.5)", value=False)
    return age_years, spanish_version


def render_question(q, responses):
    qid, qtype, label = q["id"], q["type"], q["text"]

    if qtype == "single-select":
        opts = q["options"]
        labels = [opt["label"] if isinstance(opt, dict) else str(opt) for opt in opts]
        values = [opt["value"] if isinstance(opt, dict) else opt for opt in opts]
        selected = st.selectbox(label, labels, index=None, placeholder="Select an option", key=qid)
        if selected is not None:
            responses[qid] = values[labels.index(selected)]

    elif qtype == "multi-select":
        opts = q["options"]
        labels = [opt["label"] if isinstance(opt, dict) else str(opt) for opt in opts]
        values = [opt["value"] if isinstance(opt, dict) else opt for opt in opts]
        selected_labels = st.multiselect(label, labels, key=qid)
        responses[qid] = [values[labels.index(label)] for label in selected_labels]

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
        st.markdown(f"**{label}**")
        group_answers = {}
        for item in q["items"]:
            itype, iid, itext = item["type"], item["id"], item["text"]
            if itype == "currency":
                group_answers[iid] = float(st.number_input(itext, min_value=0.0, value=0.0, step=1.0, key=iid))
            elif itype == "boolean":
                group_answers[iid] = st.checkbox(itext, value=False, key=iid)
            else:
                group_answers[iid] = st.text_input(itext, value="", key=iid)
        responses[qid] = group_answers

    elif qtype == "checklist":
        st.markdown(f"**{label}**")
        checklist_answers = {}
        for item in q["items"]:
            iid, itext = item["id"], item["label"]
            if item.get("type", "boolean") == "text":
                checklist_answers[iid] = st.text_input(itext, value="", key=iid)
            else:
                checklist_answers[iid] = st.checkbox(itext, value=False, key=iid)
        responses[qid] = checklist_answers

        if qid == "q16_unmet_needs":
            has_need = any(checklist_answers.get(iid) for iid in ["q16_food", "q16_healthy_food", "q16_healthcare", "q16_phone"])
            if has_need:
                st.markdown("**Follow-up Questions**")
                responses["q16a_medical_bills"] = st.checkbox(
                    "During the past 12 months, problems paying or unable to pay any medical bills?",
                    value=False,
                )
                responses["q16b_delayed_care_cost"] = st.checkbox(
                    "During the past 12 months, was medical care delayed because of worry about the cost?",
                    value=False,
                )
                worry_map = {
                    "Very worried": "very_worried",
                    "Moderately worried": "moderately_worried",
                    "Not too worried": "not_too_worried",
                    "Not worried at all": "not_worried",
                }
                responses["q16c_worry_housing_repeat"] = select_enum(
                    "How worried are you right now about not being able to pay your rent, mortgage, or other housing costs?",
                    worry_map,
                    default_label="Moderately worried",
                    key="q16c_worry_housing_repeat",
                )
                responses["q16d_worry_bills"] = select_enum(
                    "How worried are you right now about not being able to pay your normal monthly bills?",
                    worry_map,
                    default_label="Moderately worried",
                    key="q16d_worry_bills",
                )

    elif qtype == "matrix":
        scale, rows = q["scale"], q["rows"]
        labels = [s["label"] for s in scale]
        values = [s["value"] for s in scale]
        matrix_answers = {}
        st.markdown(f"**{label}**")
        for row in rows:
            choice = st.radio(row["label"], labels, horizontal=True, index=0, key=row["id"])
            matrix_answers[row["id"]] = values[labels.index(choice)]
        responses[qid] = matrix_answers


def compute_results(responses, age_years, spanish_version):
    phq2 = responses.get("q19a_phq2") or {}
    phq2_score = sum(int(phq2.get(k, 0)) for k in ["phq2_item1", "phq2_item2"])

    hits = responses.get("q19b_ipv_hits") or {}
    hits_score = sum(float(hits.get(k, 0)) for k in ["hits_hurt", "hits_insult", "hits_threaten", "hits_scream"])
    hits_cutoff = 5.5 if spanish_version else 10.5

    try:
        days = int(responses.get("q20a_pa_days") or 0)
    except (TypeError, ValueError):
        days = 0
    try:
        minutes = int(responses.get("q20b_pa_minutes") or 0)
    except (TypeError, ValueError):
        minutes = 0

    weekly_minutes = days * minutes
    if 6 <= age_years <= 17:
        pa_need = weekly_minutes < 420
    elif age_years >= 18:
        pa_need = weekly_minutes < 150
    else:
        pa_need = False

    unmet = responses.get("q16_unmet_needs") or {}
    return {
        "phq2_score": phq2_score,
        "depression_screen_positive": phq2_score >= 3,
        "hits_score": hits_score,
        "ipv_screen_positive": hits_score >= hits_cutoff,
        "hits_cutoff": hits_cutoff,
        "weekly_minutes_activity": weekly_minutes,
        "physical_activity_need": pa_need,
        "housing_instability": (
            responses.get("q6a_housing_situation") in ["worried_losing", "no_housing"]
            or responses.get("q6d_difficult_to_pay_housing") is True
        ),
        "transportation_need": responses.get("q15b_transport_barrier") is True,
        "food_insecurity": bool(unmet.get("q16_food") or unmet.get("q16_healthy_food")),
        "medical_cost_barrier": bool(responses.get("q16a_medical_bills") or responses.get("q16b_delayed_care_cost")),
        "age_years": age_years,
        "spanish_version": spanish_version,
    }


def main():
    cfg = load_cfg()
    schema = load_schema()
    questions = cfg["screener"]["questions"]

    st.markdown(
        """
        <div class="hero">
            <h1>SDoH Screener</h1>
            <p>Complete this structured screening form to identify social needs and support referrals.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel">Questions are generated dynamically from JSON configuration and validated against the schema on submit.</div>', unsafe_allow_html=True)

    age_years, spanish_version = render_sidebar()

    st.subheader("Questionnaire")
    with st.form("sdoh_form"):
        responses = {}
        for q in questions:
            if check_visible_if(q.get("visible_if"), responses):
                render_question(q, responses)
        submitted = st.form_submit_button("Submit and Validate")

    if not submitted:
        return

    st.subheader("Validation")
    responses = normalize_values(responses)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(responses), key=lambda e: list(e.path))

    if errors:
        st.error("Validation failed. Please review the fields below.")
        for error in errors:
            st.write(f"• At {list(error.path)}: {error.message}")
        return

    st.success("Schema validation passed ✅")

    results = compute_results(responses, age_years, spanish_version)

    st.subheader("Computed Scores & Flags")
    col1, col2, col3 = st.columns(3)
    col1.metric("PHQ-2 Score", f"{results['phq2_score']}")
    col2.metric("HITS Score", f"{results['hits_score']:.1f}")
    col3.metric("Weekly Activity Minutes", f"{results['weekly_minutes_activity']}")
    st.write(pd.DataFrame([results]).T.rename(columns={0: "value"}))

    if results["ipv_screen_positive"]:
        st.error("Safety notice: responses suggest possible IPV risk.")
        st.markdown(
            """
- **EU emergency number:** **112** (free, 24/7).
- **Greece police:** **100**.
- **Women SOS hotline (Greece):** **15900** (`sos15900@isotita.gr`).
            """
        )

    st.markdown("### Interpretation for Researchers")
    st.markdown(
        """
- `phq2_score` ≥ 3 indicates a positive depression screen.
- `ipv_screen_positive` is based on language-specific HITS cutoff (10.5 default, 5.5 Spanish).
- `physical_activity_need` is true if weekly activity is below age-based thresholds.
- Social need flags include housing instability, transportation need, food insecurity, and medical cost barriers.
        """
    )

    st.subheader("Submitted Payload")
    st.json(responses)
    st.download_button("Download responses.json", data=json.dumps(responses, indent=2), file_name="responses.json")
    st.download_button("Download results.json", data=json.dumps(results, indent=2), file_name="results.json")


if __name__ == "__main__":
    main()
