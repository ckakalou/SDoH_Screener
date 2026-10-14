import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from jsonschema import Draft202012Validator, FormatChecker

from backend.app.models import ScreenerSubmission, ValidationResult


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCREENER_FILE = PROJECT_ROOT / "sdoh_screener_eu_gr_v2.json"
RESPONSE_SCHEMA_FILE = (
    PROJECT_ROOT / "sdoh_screener_response_schema_eu_gr_v2.json"
)
INDICATOR_SCHEMA_FILE = PROJECT_ROOT / "healie_indicator_export_schema_v1.json"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"


def load_json_file(file_path: Path) -> dict[str, Any]:
    with file_path.open(encoding="utf-8") as file:
        return json.load(file)


SCREENER_DATA = load_json_file(SCREENER_FILE)
RESPONSE_SCHEMA = load_json_file(RESPONSE_SCHEMA_FILE)
INDICATOR_SCHEMA = load_json_file(INDICATOR_SCHEMA_FILE)

Draft202012Validator.check_schema(RESPONSE_SCHEMA)
Draft202012Validator.check_schema(INDICATOR_SCHEMA)
response_validator = Draft202012Validator(RESPONSE_SCHEMA)
indicator_validator = Draft202012Validator(
    INDICATOR_SCHEMA,
    format_checker=FormatChecker(),
)
SCREENER_QUESTIONS = SCREENER_DATA["screener"]["questions"]


app = FastAPI(
    title="HEALIE SD-DOH Assessment API",
    description=(
        "Backend API for the EU/Greek Social and Digital Determinants "
        "of Health assessment."
    ),
    version="0.4.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/screener")
def get_screener() -> dict[str, Any]:
    return SCREENER_DATA


def get_answer(question_id: str, responses: dict[str, Any]) -> Any:
    if question_id in responses:
        return responses[question_id]

    for answer in responses.values():
        if isinstance(answer, dict) and question_id in answer:
            return answer[question_id]

    return None


def condition_matches(
    condition: dict[str, Any],
    responses: dict[str, Any],
) -> bool:
    answer = get_answer(condition["question"], responses)
    operator = condition.get("operator")

    if operator == "=":
        return answer == condition.get("value")

    if operator == "contains":
        return isinstance(answer, list) and condition.get("value") in answer

    return False


def is_question_visible(
    question: dict[str, Any],
    responses: dict[str, Any],
) -> bool:
    rule = question.get("visible_if")

    if not rule:
        return True

    any_conditions = rule.get("any")
    all_conditions = rule.get("all")

    any_matches = (
        any(condition_matches(condition, responses) for condition in any_conditions)
        if any_conditions
        else True
    )
    all_match = (
        all(condition_matches(condition, responses) for condition in all_conditions)
        if all_conditions
        else True
    )

    return any_matches and all_match


def is_optional_question(question: dict[str, Any]) -> bool:
    return question.get("required", True) is False


def validate_exclusive_answer(
    question: dict[str, Any],
    responses: dict[str, Any],
) -> None:
    exclusive_item_id = question.get("exclusive_item_id")
    exclusive_item_ids = set(question.get("exclusive_item_ids", []))
    if exclusive_item_id:
        exclusive_item_ids.add(exclusive_item_id)
    answer = responses.get(question["id"])

    if exclusive_item_ids and isinstance(answer, dict):
        selected_exclusive_items = [
            item_id for item_id in exclusive_item_ids if answer.get(item_id) is True
        ]
        if selected_exclusive_items:
            answered_regular_items = [
                item["id"]
                for item in question.get("items", [])
                if item["id"] not in exclusive_item_ids and item["id"] in answer
            ]

            if answered_regular_items or len(selected_exclusive_items) > 1:
                exclusive_fields = ", ".join(sorted(selected_exclusive_items))
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"{question['id']}.{exclusive_fields}: "
                        "An exclusive option cannot be "
                        "combined with another checklist response."
                    ),
                )

    exclusive_option = question.get("exclusive_option_value")
    exclusive_options = set(question.get("exclusive_option_values", []))
    if exclusive_option:
        exclusive_options.add(exclusive_option)

    if (
        exclusive_options
        and isinstance(answer, list)
        and any(option in answer for option in exclusive_options)
        and (
            len(answer) > 1
            or sum(option in answer for option in exclusive_options) > 1
        )
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                f"{question['id']}: An exclusive option cannot be combined "
                "with another selected option."
            ),
        )


def total_matrix_answer(
    responses: dict[str, Any],
    question_id: str,
) -> int | None:
    answer = responses.get(question_id)

    if not isinstance(answer, dict) or not answer:
        return None

    return sum(answer.values())


def assessment_status(
    value: Any,
    *,
    declined_values: set[Any] | None = None,
    uncertain_values: set[Any] | None = None,
) -> str:
    if value is None or value == "" or value == []:
        return "not_assessed"
    if declined_values and value in declined_values:
        return "declined"
    if uncertain_values and value in uncertain_values:
        return "uncertain"
    return "assessed"


def nullable_value(value: Any, status: str) -> Any:
    return value if status == "assessed" else None


def frequency_barrier(value: Any) -> bool | None:
    if value in {"sometimes", "never"}:
        return True
    if value in {"always", "often"}:
        return False
    return None


def calculate_internet_access_level(
    household_access: bool | None,
    household_status: str,
    personal_connectivity: Any,
) -> str | None:
    if personal_connectivity in {None, "prefer_not_answer"}:
        return None

    has_fixed_home_access = household_access is True
    lacks_fixed_home_access = (
        household_access is False or household_status == "not_applicable"
    )

    if personal_connectivity in {"always", "often"}:
        return (
            "reliable_home_supported"
            if has_fixed_home_access
            else "reliable_non_home_or_mobile"
        )
    if personal_connectivity == "sometimes":
        if has_fixed_home_access:
            return "intermittent_despite_home_access"
        if household_status == "not_applicable":
            return "intermittent_without_fixed_home_access"
        return "intermittent_without_home_access"
    if personal_connectivity == "never":
        if has_fixed_home_access:
            return "home_access_not_usable_for_digital_health"
        if lacks_fixed_home_access:
            return "no_usable_access"
    return None


def calculate_derived_results(responses: dict[str, Any]) -> dict[str, Any]:
    declined = {"prefer_not_answer", "prefer_not_to_say", "decline"}

    age_value = responses.get("dem_age_group")
    age_status = assessment_status(age_value, declined_values=declined)
    life_stage_map = {
        "16_17": "adolescent",
        "18_21": "young_adult",
        "22_30": "young_adult",
        "31_40": "adult",
        "41_50": "adult",
        "51_60": "adult",
        "61_70": "older_adult",
        "71_80": "older_adult",
        "81_plus": "older_adult",
    }

    gender = responses.get("dem_gender")
    gender_status = assessment_status(gender, declined_values=declined)
    ethnic_groups = responses.get("q1_ethnic_group")
    ethnic_status = assessment_status(ethnic_groups)
    region = responses.get("q2_europe_region")
    region_status = assessment_status(region, declined_values=declined)
    ancestry = responses.get("q2_ancestry")
    ancestry_status = assessment_status(ancestry)

    income = responses.get("q3_household_income")
    income_status = assessment_status(income, declined_values=declined)

    education = responses.get("q4_education")
    education_status = assessment_status(education, declined_values=declined)
    education_group_map = {
        "no_formal": "below_secondary",
        "primary": "below_secondary",
        "lower_secondary": "below_secondary",
        "upper_secondary": "secondary",
        "vocational": "vocational",
        "undergraduate": "tertiary",
        "masters": "tertiary",
        "doctorate": "tertiary",
    }

    work_status = responses.get("q5_work_status")
    work_assessment = assessment_status(work_status, declined_values=declined)
    current_paid_work = {"full_time", "part_time", "self_employed"}
    outside_paid_work = {
        "unemployed", "homemaker", "student", "retired", "unable_disability"
    }
    if work_status in current_paid_work:
        paid_work_group = "current_paid_work"
    elif work_status in outside_paid_work:
        paid_work_group = "not_currently_in_paid_work"
    elif work_status == "other":
        paid_work_group = "other_or_unclassified"
    else:
        paid_work_group = None
    last_worked = responses.get("q5b_last_worked")
    unemployment_duration = None
    if work_status == "unemployed":
        unemployment_duration = {
            "past_12_months": "short_term",
            "one_to_five_years": "long_term",
            "over_five_or_never": "long_term_or_never_worked",
        }.get(last_worked)

    housing_situation = responses.get("q6a_housing_situation")
    housing_status = assessment_status(housing_situation, declined_values=declined)
    stability_map = {
        "have_housing": "stable",
        "worried_losing": "at_risk",
        "no_housing": "unhoused",
    }
    tenure = responses.get("q6b_tenure")

    coverage = responses.get("q10_health_coverage")
    coverage_status = assessment_status(
        coverage,
        declined_values=declined,
        uncertain_values={"not_sure"},
    )
    coverage_value = "none_reported" if coverage == "no_coverage" else coverage

    postal_code = responses.get("q9b_longest_zip")
    postal_status = assessment_status(postal_code)

    if housing_situation == "no_housing":
        home_internet_status = "not_applicable"
        household_home_internet = None
    else:
        household_home_internet = responses.get("q11_internet")
        home_internet_status = assessment_status(household_home_internet)
    personal_connectivity = responses.get("ddoh_connectivity")
    personal_connectivity_status = assessment_status(
        personal_connectivity, declined_values=declined
    )
    digital_connectivity_status = (
        "declined"
        if personal_connectivity_status == "declined"
        else (
            "assessed"
            if personal_connectivity_status == "assessed"
            else "not_assessed"
        )
    )

    language = responses.get("q13_local_language_proficiency")
    language_status = assessment_status(language)

    marital_status = responses.get("q14a_marital_status")
    family_status = assessment_status(marital_status, declined_values=declined)

    transport_mode = responses.get("q15a_commute_mode")
    transport_answers = responses.get("q15b_transport_barrier")
    transport_status = assessment_status(transport_answers)
    if isinstance(transport_answers, list) and "prefer_not_answer" in transport_answers:
        transport_status = "declined"

    social_contact = responses.get("q17_social_connections")
    social_status = assessment_status(social_contact, declined_values=declined)
    neighbourhood_support = responses.get("q18_neighborhood_support")
    neighbourhood_status = assessment_status(neighbourhood_support)
    cognition = responses.get("q19d_cognition_selfreport")
    cognition_status = assessment_status(cognition, declined_values=declined)
    cognition_map = {
        "no": "none_reported",
        "yes_some": "mild_or_sometimes",
        "yes_often": "frequent_or_significant",
    }

    context: dict[str, Any] = {
        "age": {
            "assessment_status": age_status,
            "age_band": nullable_value(age_value, age_status),
            "life_stage": life_stage_map.get(age_value),
        },
        "identity": {
            "gender": {
                "assessment_status": gender_status,
                "category": nullable_value(gender, gender_status),
            },
            "ethnic_group": {
                "assessment_status": ethnic_status,
                "categories": ethnic_groups if ethnic_status == "assessed" else None,
            },
            "regional_origin": {
                "assessment_status": region_status,
                "european_region": nullable_value(region, region_status),
            },
            "ancestry": {
                "assessment_status": ancestry_status,
                "reported_value": nullable_value(ancestry, ancestry_status),
            },
        },
        "economic": {
            "assessment_status": income_status,
            "household_income_band": nullable_value(income, income_status),
        },
        "education": {
            "assessment_status": education_status,
            "attainment_group": education_group_map.get(education),
            "attainment_detail": nullable_value(education, education_status),
        },
        "employment": {
            "assessment_status": work_assessment,
            "current_status": nullable_value(work_status, work_assessment),
            "paid_work_group": paid_work_group,
            "last_worked": last_worked,
            "unemployment_duration": unemployment_duration,
        },
        "housing": {
            "assessment_status": housing_status,
            "stability": stability_map.get(housing_situation),
            "tenure": tenure,
        },
        "health_coverage": {
            "assessment_status": coverage_status,
            "reported_coverage": nullable_value(coverage_value, coverage_status),
        },
        "geographic_linkage": {
            "assessment_status": postal_status,
            "postal_code": nullable_value(postal_code, postal_status),
        },
        "digital_connectivity": {
            "assessment_status": digital_connectivity_status,
            "household_home_internet": household_home_internet,
            "household_home_internet_status": home_internet_status,
            "personal_connectivity": nullable_value(
                personal_connectivity, personal_connectivity_status
            ),
            "internet_access_level": calculate_internet_access_level(
                household_home_internet,
                home_internet_status,
                personal_connectivity,
            ),
        },
        "language_access": {
            "assessment_status": language_status,
            "speaking_proficiency": nullable_value(language, language_status),
        },
        "family": {
            "assessment_status": family_status,
            "marital_status": nullable_value(marital_status, family_status),
            "single_parent": responses.get("q14b_single_parent"),
        },
        "transportation": {
            "assessment_status": assessment_status(transport_mode),
            "usual_travel_mode": transport_mode,
        },
        "social_connection": {
            "assessment_status": social_status,
            "contact_frequency": nullable_value(social_contact, social_status),
        },
        "neighbourhood_support": {
            "assessment_status": neighbourhood_status,
            "perceived_support": nullable_value(
                neighbourhood_support, neighbourhood_status
            ),
        },
        "cognitive_function": {
            "assessment_status": cognition_status,
            "self_reported_daily_life_impact": cognition_map.get(cognition),
        },
    }

    housing_worry_values = {
        responses.get("q6e_worry_housing_costs"),
        responses.get("q16c_worry_housing_repeat"),
    }
    housing_cost_concern = (
        True
        if housing_worry_values & {"very_worried", "moderately_worried"}
        else (
            False
            if housing_worry_values & {"not_too_worried", "not_worried"}
            else None
        )
    )
    payment_difficulty = responses.get("q6d_difficult_to_pay_housing")
    affordability_need = (
        True
        if payment_difficulty is True or housing_cost_concern is True
        else (
            False
            if payment_difficulty is False or housing_cost_concern is False
            else None
        )
    )

    disability_answers = responses.get("q12_disability")
    functional_domain_map = {
        "q12a_hearing": "hearing",
        "q12b_vision": "vision",
        "q12c_cognitive": "cognition",
        "q12d_mobility": "mobility",
        "q12e_adl": "self_care",
        "q12f_iadl": "independent_living",
    }
    reported_difficulties = (
        [
            domain
            for item, domain in functional_domain_map.items()
            if disability_answers.get(item) is True
        ]
        if isinstance(disability_answers, dict)
        else None
    )

    unmet_answers = responses.get("q16_unmet_needs")
    unmet_domain_map = {
        "q16_food": "food",
        "q16_healthy_food": "healthy_food",
        "q16_healthcare": "healthcare",
        "q16_phone": "phone",
    }
    if isinstance(unmet_answers, dict) and unmet_answers.get("q16_decline") is True:
        material_status = "declined"
        unmet_domains = None
    elif isinstance(unmet_answers, dict):
        material_status = "assessed"
        unmet_domains = [
            domain
            for item, domain in unmet_domain_map.items()
            if unmet_answers.get(item) is True
        ]
    else:
        material_status = "not_assessed"
        unmet_domains = None

    days_answer = responses.get("q20a_pa_days")
    minutes_answer = responses.get("q20b_pa_minutes")
    weekly_minutes = None
    activity_need = None
    activity_status = assessment_status(days_answer)
    if days_answer is not None:
        days = int(days_answer)
        weekly_minutes = 0 if days == 0 else days * int(minutes_answer or 0)
        if age_status == "assessed":
            threshold = 420 if age_value == "16_17" else 150
            activity_need = weekly_minutes < threshold
        else:
            activity_status = "not_assessed"

    legal_need = responses.get("legal_need")
    legal_domains = responses.get("legal_need_domains")
    legal_support = responses.get("legal_support_access")
    legal_unmet: bool | None = None
    if legal_need == "no":
        legal_status = "assessed"
        exported_legal_domains: list[str] | None = []
        legal_unmet = False
    elif legal_need == "yes":
        legal_status = "assessed"
        exported_legal_domains = (
            [value for value in legal_domains if value != "prefer_not_answer"]
            if isinstance(legal_domains, list)
            else None
        )
        if legal_support in {
            "some_not_enough", "tried_none", "did_not_know_where",
            "cost_or_access_barrier",
        }:
            legal_unmet = True
        elif legal_support in {"all_support", "chose_not_to_seek"}:
            legal_unmet = False
    elif legal_need == "not_sure":
        legal_status = "uncertain"
        exported_legal_domains = (
            [value for value in legal_domains if value != "prefer_not_answer"]
            if isinstance(legal_domains, list)
            else None
        )
    elif legal_need == "prefer_not_answer":
        legal_status = "declined"
        exported_legal_domains = None
    else:
        legal_status = "not_assessed"
        exported_legal_domains = None

    needs: dict[str, Any] = {
        "housing": {
            "stability_need": (
                housing_situation in {"worried_losing", "no_housing"}
                if housing_status == "assessed"
                else None
            ),
            "affordability_need": affordability_need,
        },
        "functional_access": {
            "assessment_status": (
                "assessed" if reported_difficulties is not None else "not_assessed"
            ),
            "reported_difficulty_domains": reported_difficulties,
        },
        "language_support": {
            "indicated": (
                language in {"not_well", "not_at_all"}
                if language_status == "assessed"
                else None
            )
        },
        "transportation": {
            "assessment_status": transport_status,
            "barrier_reported": (
                any(
                    domain in transport_answers
                    for domain in {"healthcare", "daily_living"}
                )
                if isinstance(transport_answers, list)
                and transport_status == "assessed"
                else None
            ),
            "healthcare_access_affected": (
                "healthcare" in transport_answers
                if isinstance(transport_answers, list)
                and transport_status == "assessed"
                else None
            ),
            "daily_living_access_affected": (
                "daily_living" in transport_answers
                if isinstance(transport_answers, list)
                and transport_status == "assessed"
                else None
            ),
        },
        "material_needs": {
            "assessment_status": material_status,
            "unmet_domains": unmet_domains,
        },
        "healthcare_affordability": {
            "medical_bill_payment_problem": responses.get("q16a_medical_bills"),
            "care_delayed_due_to_cost": responses.get("q16b_delayed_care_cost"),
        },
        "financial_strain": {
            "housing_cost_concern_identified": housing_cost_concern,
            "monthly_bill_concern_identified": (
                responses.get("q16d_worry_bills")
                in {"very_worried", "moderately_worried"}
                if responses.get("q16d_worry_bills") is not None
                else None
            ),
        },
        "physical_activity": {
            "assessment_status": activity_status,
            "weekly_minutes": weekly_minutes,
            "need_identified": activity_need,
        },
        "legal_support": {
            "assessment_status": legal_status,
            "domains": exported_legal_domains,
            "unmet_need_identified": legal_unmet,
        },
        "digital_access": {
            "device_access_barrier": frequency_barrier(
                responses.get("ddoh_device_access")
            ),
            "connectivity_barrier": frequency_barrier(personal_connectivity),
            "affordability_barrier": (
                True if responses.get("ddoh_affordability") == "yes"
                else False if responses.get("ddoh_affordability") == "no"
                else None
            ),
            "accessibility_barrier": frequency_barrier(
                responses.get("ddoh_accessibility")
            ),
            "support_barrier": (
                True if responses.get("ddoh_support") in {"sometimes", "never"}
                else False if responses.get("ddoh_support") in {
                    "always", "often", "no_assistance_needed"
                }
                else None
            ),
            "privacy_trust_barrier": (
                True if responses.get("ddoh_privacy_trust") == "yes"
                else False if responses.get("ddoh_privacy_trust") == "no"
                else None
            ),
        },
    }

    depression_score = total_matrix_answer(responses, "q19a_phq2")
    anxiety_score = total_matrix_answer(responses, "q19c_gad2")
    screening_results = {
        "depression": {
            "assessment_status": (
                "declined"
                if responses.get("q19a_phq2_participation") == "decline"
                else "assessed" if depression_score is not None else "not_assessed"
            ),
            "instrument": "phq_2",
            "score": depression_score,
            "screen_positive": (
                depression_score >= 3 if depression_score is not None else None
            ),
        },
        "anxiety": {
            "assessment_status": (
                "declined"
                if responses.get("q19c_gad2_participation") == "decline"
                else "assessed" if anxiety_score is not None else "not_assessed"
            ),
            "instrument": "gad_2",
            "score": anxiety_score,
            "screen_positive": (
                anxiety_score >= 3 if anxiety_score is not None else None
            ),
        },
    }

    hits_score = total_matrix_answer(responses, "q19b_ipv_hits")
    restricted_safety_indicators = {
        "ipv": {
            "assessment_status": (
                "assessed" if hits_score is not None else "not_assessed"
            ),
            "instrument": "hits",
            "score": hits_score,
            "screen_positive": hits_score >= 11 if hits_score is not None else None,
        }
    }

    return {
        "assessment_id": str(uuid4()),
        "schema_version": "healie-sdoh-ddoh-indicators-1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "context": context,
        "needs": needs,
        "screening_results": screening_results,
        "restricted_safety_indicators": restricted_safety_indicators,
    }


def is_answer_complete(
    question: dict[str, Any],
    responses: dict[str, Any],
) -> tuple[bool, str | None]:
    question_id = question["id"]
    answer = responses.get(question_id)

    if answer is None or answer == "":
        return False, question_id

    if isinstance(answer, list) and not answer:
        return False, question_id

    if question["type"] == "checklist":
        if not isinstance(answer, dict):
            return False, question_id

        exclusive_item_id = question.get("exclusive_item_id")

        if exclusive_item_id and answer.get(exclusive_item_id) is True:
            return True, None

        for item in question.get("items", []):
            if item["id"] not in answer:
                return False, item["id"]

    if question["type"] == "matrix":
        if not isinstance(answer, dict):
            return False, question_id

        for row in question.get("rows", []):
            if row["id"] not in answer:
                return False, row["id"]

    return True, None


def validate_completion(
    responses: dict[str, Any],
    section: int | None,
) -> None:
    for question in SCREENER_QUESTIONS:
        if section is not None and question["section"] != section:
            continue

        if not is_question_visible(question, responses):
            continue

        validate_exclusive_answer(question, responses)

        if is_optional_question(question):
            continue

        is_complete, missing_field = is_answer_complete(question, responses)

        if not is_complete:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"{missing_field}: Please answer every visible question "
                    "before continuing."
                ),
            )


@app.post(
    "/api/v1/screener/validate",
    response_model=ValidationResult,
)
def validate_screener(
    submission: ScreenerSubmission,
) -> ValidationResult:
    errors = sorted(
        response_validator.iter_errors(submission.responses),
        key=lambda error: list(error.absolute_path),
    )

    if errors:
        first_error = errors[0]
        field = ".".join(str(part) for part in first_error.absolute_path)
        location = field or "responses"

        raise HTTPException(
            status_code=422,
            detail=f"{location}: {first_error.message}",
        )

    validate_completion(submission.responses, submission.section)

    if submission.section is not None:
        return ValidationResult(
            valid=True,
            message="The section responses are valid.",
        )

    derived = calculate_derived_results(submission.responses)
    indicator_validator.validate(derived)

    return ValidationResult(
        valid=True,
        message="The screener responses are valid.",
        derived=derived,
    )


if FRONTEND_INDEX.is_file():

    @app.get("/{requested_path:path}", include_in_schema=False)
    def serve_frontend(requested_path: str) -> FileResponse:
        """Serve the Vite production build while preserving API routes."""
        if requested_path == "api" or requested_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found.")

        frontend_root = FRONTEND_DIST.resolve()
        requested_file = (FRONTEND_DIST / requested_path).resolve()

        if requested_path:
            try:
                requested_file.relative_to(frontend_root)
            except ValueError:
                requested_file = FRONTEND_INDEX

        if requested_path and requested_file.is_file():
            return FileResponse(requested_file)

        return FileResponse(FRONTEND_INDEX)
