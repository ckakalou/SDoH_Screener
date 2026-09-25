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

    return ValidationResult(
        valid=True,
        message="The screener responses are valid.",
    )
