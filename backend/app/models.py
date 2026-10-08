# Created by Christine Kakalou on 10/9/26
# Project: SDoH_Screener

from typing import Any

from pydantic import BaseModel, Field


class ScreenerSubmission(BaseModel):
    responses: dict[str, Any] = Field(
        description="Answers keyed by their questionnaire identifiers."
    )
    section: int | None = Field(
        default=None,
        ge=1,
        description=(
            "When supplied, completeness is checked only for this section. "
            "When omitted, the full visible screener is checked."
        ),
    )


class ValidationResult(BaseModel):
    valid: bool
    message: str
    derived: dict[str, Any] = Field(default_factory=dict)
