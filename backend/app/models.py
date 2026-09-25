# Created by Christine Kakalou on 10/9/26
# Project: SDoH_Screener

from typing import Any

from pydantic import BaseModel, Field


class ScreenerSubmission(BaseModel):
    responses: dict[str, Any] = Field(
        description="Answers keyed by their questionnaire identifiers."
    )


class ValidationResult(BaseModel):
    valid: bool
    message: str

