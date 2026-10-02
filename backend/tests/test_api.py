# Created by Christine Kakalou on 10/9/26
# Project: SDoH_Screener

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_screener() -> None:
    response = client.get("/api/v1/screener")

    assert response.status_code == 200

    data = response.json()
    screener = data["screener"]

    assert screener["version"] == "2.0.0-eu-gr"
    assert screener["title"] == (
        "Social Determinants of Health (SDoH) Screener – EU/GR Adaptation"
    )
    assert isinstance(screener["questions"], list)
    assert len(screener["questions"]) > 0

def test_validate_valid_responses() -> None:
    response = client.post(
        "/api/v1/screener/validate",
        json={
            "responses": {
                "q3_household_income": "20000_29999",
            },
            "section": 3,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "message": "The screener responses are valid.",
    }


def test_validate_invalid_responses() -> None:
    response = client.post(
        "/api/v1/screener/validate",
        json={
            "responses": {
                "q20a_pa_days": "1",
                "q20b_pa_minutes": 25,
            },
            "section": 20,
        },
    )

    assert response.status_code == 422
    assert "q20b_pa_minutes" in response.json()["detail"]


def test_validate_missing_visible_question() -> None:
    response = client.post(
        "/api/v1/screener/validate",
        json={
            "responses": {
                "q9a_residence_length": "lt6mo",
                "q9b_longest_zip": "5555",
            },
            "section": 9,
        },
    )

    assert response.status_code == 422
    assert "q9c_multiple_residences" in response.json()["detail"]


def test_validate_incomplete_checklist() -> None:
    response = client.post(
        "/api/v1/screener/validate",
        json={
            "responses": {
                "q12_disability": {
                    "q12a_hearing": False,
                    "q12b_vision": True,
                    "q12c_cognitive": False,
                    "q12e_adl": False,
                    "q12f_iadl": False,
                }
            },
            "section": 12,
        },
    )

    assert response.status_code == 422
    assert "q12d_mobility" in response.json()["detail"]


def test_validate_optional_question_can_be_empty() -> None:
    response = client.post(
        "/api/v1/screener/validate",
        json={"responses": {}, "section": 1},
    )

    assert response.status_code == 200


def test_validate_hidden_conditional_question_is_not_required() -> None:
    response = client.post(
        "/api/v1/screener/validate",
        json={
            "responses": {
                "q21_religion_spiritual_belief": "greek_orthodox",
            },
            "section": 21,
        },
    )

    assert response.status_code == 200


def test_validate_visible_conditional_question_is_required() -> None:
    response = client.post(
        "/api/v1/screener/validate",
        json={
            "responses": {
                "q21_religion_spiritual_belief": "other",
            },
            "section": 21,
        },
    )

    assert response.status_code == 422
    assert "q21a_religion_other_text" in response.json()["detail"]
