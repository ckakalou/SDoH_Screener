import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from jsonschema import Draft202012Validator

from backend.app.models import ScreenerSubmission, ValidationResult


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCREENER_FILE = PROJECT_ROOT / "sdoh_screener_eu_gr_v2.json"
RESPONSE_SCHEMA_FILE = (
    PROJECT_ROOT / "sdoh_screener_response_schema_eu_gr_v2.json"
)


def load_json_file(file_path: Path) -> dict[str, Any]:
    with file_path.open(encoding="utf-8") as file:
        return json.load(file)


SCREENER_DATA = load_json_file(SCREENER_FILE)
RESPONSE_SCHEMA = load_json_file(RESPONSE_SCHEMA_FILE)

Draft202012Validator.check_schema(RESPONSE_SCHEMA)
response_validator = Draft202012Validator(RESPONSE_SCHEMA)
SCREENER_QUESTIONS = SCREENER_DATA["screener"]["questions"]


app = FastAPI(
    title="HEALIE SD-DOH Assessment API",
    description=(
        "Backend API for the EU/Greek Social and Digital Determinants "
        "of Health assessment."
    ),
    version="0.3.0",
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
    answer = responses.get(question["id"])

    if exclusive_item_id and isinstance(answer, dict):
        if answer.get(exclusive_item_id) is True:
            answered_regular_items = [
                item["id"]
                for item in question.get("items", [])
                if item["id"] != exclusive_item_id and item["id"] in answer
            ]

            if answered_regular_items:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"{exclusive_item_id}: A decline option cannot be "
                        "combined with answers to the other checklist items."
                    ),
                )

    exclusive_option = question.get("exclusive_option_value")

    if (
        exclusive_option
        and isinstance(answer, list)
        and exclusive_option in answer
        and len(answer) > 1
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                f"{question['id']}: {exclusive_option} cannot be combined "
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


def calculate_derived_results(responses: dict[str, Any]) -> dict[str, Any]:
    derived: dict[str, Any] = {}

    for question_id, score_key, flag_key, threshold in (
        ("q19a_phq2", "phq2_score", "depression_screen_positive", 3),
        ("q19b_ipv_hits", "hits_score", "ipv_screen_positive", 11),
        ("q19c_gad2", "gad2_score", "anxiety_screen_positive", 3),
    ):
        total = total_matrix_answer(responses, question_id)
        if total is not None:
            derived[score_key] = total
            derived[flag_key] = total >= threshold

    days_answer = responses.get("q20a_pa_days")
    minutes_answer = responses.get("q20b_pa_minutes")

    if days_answer is not None:
        days = int(days_answer)
        weekly_minutes = 0 if days == 0 else days * int(minutes_answer or 0)
        derived["weekly_minutes_activity"] = weekly_minutes

        age_group = responses.get("dem_age_group")
        if age_group in (None, "prefer_not_answer"):
            derived["physical_activity_need"] = "not_assessed"
        else:
            threshold = 420 if age_group == "16_17" else 150
            derived["physical_activity_need"] = weekly_minutes < threshold

    legal_need = responses.get("legal_need")
    if legal_need is not None:
        derived["legal_need_assessment"] = legal_need
        domains = responses.get("legal_need_domains")
        if isinstance(domains, list):
            derived["legal_need_domains"] = domains

        support = responses.get("legal_support_access")
        if support is not None:
            derived["legal_support_access"] = support
            derived["potential_unmet_legal_need"] = support in {
                "some_not_enough",
                "tried_none",
                "did_not_know_where",
                "cost_or_access_barrier",
            }

    return derived


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

    return ValidationResult(
        valid=True,
        message="The screener responses are valid.",
        derived=calculate_derived_results(submission.responses),
    )
