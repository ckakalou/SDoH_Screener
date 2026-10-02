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
    title="SDoH Screener API",
    description="Backend API for the EU/Greek Social Determinants of Health screener.",
    version="0.1.0",
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
    if condition.get("operator") != "=":
        return False

    return get_answer(condition["question"], responses) == condition.get(
        "value"
    )


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
    return "optional" in question["text"].lower()


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
    )
