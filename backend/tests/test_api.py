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
                "q11_internet": True,
                "q20b_pa_minutes": 30,
                "q23_digital_device_access": "yes",
            }
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
                "q20b_pa_minutes": 25,
            }
        },
    )

    assert response.status_code == 422
    assert "q20b_pa_minutes" in response.json()["detail"]
