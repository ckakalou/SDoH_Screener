from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def validate(responses: dict, section: int | None = None):
    payload: dict = {"responses": responses}
    if section is not None:
        payload["section"] = section
    return client.post("/api/v1/screener/validate", json=payload)


def section_16_checklist(**changes: bool) -> dict[str, bool]:
    answer = {
        "q16_food": False, "q16_healthy_food": False,
        "q16_healthcare": False, "q16_phone": False,
        "q16_decline": False,
    }
    answer.update(changes)
    return answer


def test_health_check() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_get_screener_returns_refactored_assessment() -> None:
    response = client.get("/api/v1/screener")
    assert response.status_code == 200
    screener = response.json()["screener"]
    ids = {question["id"] for question in screener["questions"]}
    assert screener["version"] == "3.0.0-eu-gr"
    assert "Social and Digital Determinants of Health" in screener["title"]
    assert {"dem_age_group", "legal_need", "ddoh_privacy_trust"} <= ids
    assert "q21_religion_spiritual_belief" not in ids


def test_all_questions_have_explicit_required_metadata() -> None:
    questions = client.get("/api/v1/screener").json()["screener"]["questions"]
    assert all("required" in question for question in questions)
    assert {q["id"] for q in questions if q["required"] is False} == {
        "dem_gender", "q1_ethnic_group", "q2_ancestry",
        "q9b_longest_zip", "q19e_mmse_total",
    }


def test_age_is_required_but_optional_identity_items_are_not() -> None:
    missing = validate({}, section=1)
    assert missing.status_code == 422
    assert "dem_age_group" in missing.json()["detail"]
    assert validate({"dem_age_group": "22_30"}, section=1).status_code == 200


def test_multi_select_other_uses_contains_visibility() -> None:
    response = validate(
        {"dem_age_group": "31_40", "q1_ethnic_group": ["white", "other"]},
        section=1,
    )
    assert response.status_code == 422
    assert "q1_ethnic_group_other_text" in response.json()["detail"]


def test_work_follow_up_is_conditional() -> None:
    response = validate({"q5_work_status": "student"}, section=5)
    assert response.status_code == 422
    assert "q5b_last_worked" in response.json()["detail"]


def test_housing_cost_questions_only_apply_to_rent_or_mortgage() -> None:
    response = validate({
        "q6a_housing_situation": "have_housing",
        "q6b_tenure": "owned_free_clear",
        "q6e_worry_housing_costs": "not_worried",
    }, section=6)
    assert response.status_code == 200


def test_incomplete_disability_checklist_is_rejected() -> None:
    response = validate({"q12_disability": {
        "q12a_hearing": False, "q12b_vision": True,
        "q12c_cognitive": False, "q12e_adl": False,
        "q12f_iadl": False,
    }}, section=12)
    assert response.status_code == 422


def test_any_reported_unmet_need_requires_all_original_follow_ups() -> None:
    response = validate(
        {"q16_unmet_needs": section_16_checklist(q16_food=True)}, section=16
    )
    assert response.status_code == 422
    assert "q16a_medical_bills" in response.json()["detail"]


def test_all_original_unmet_need_follow_ups_complete_section() -> None:
    response = validate({
        "q16_unmet_needs": section_16_checklist(q16_food=True),
        "q16a_medical_bills": False,
        "q16b_delayed_care_cost": False,
        "q16c_worry_housing_repeat": "not_worried",
        "q16d_worry_bills": "not_too_worried",
    }, section=16)
    assert response.status_code == 200


def test_declining_unmet_needs_hides_follow_ups() -> None:
    response = validate(
        {"q16_unmet_needs": {"q16_decline": True}}, section=16
    )
    assert response.status_code == 200


def test_decline_cannot_be_combined_with_checklist_answers() -> None:
    response = validate({
        "q16_unmet_needs": {"q16_food": False, "q16_decline": True}
    }, section=16)
    assert response.status_code == 422
    assert "q16_decline" in response.json()["detail"]


def test_scale_participation_controls_visibility_and_scoring() -> None:
    declined = validate({
        "q19a_phq2_participation": "decline",
        "q19b_partner_status": "no",
        "q19c_gad2_participation": "decline",
        "q19d_cognition_selfreport": "no",
    }, section=19)
    assert declined.status_code == 200
    assert "phq2_score" not in declined.json()["derived"]

    scored = validate({
        "q19a_phq2_participation": "answer",
        "q19a_phq2": {"phq2_item1": 2, "phq2_item2": 1},
        "q19b_partner_status": "yes",
        "q19b_ipv_hits": {"hits_hurt": 1, "hits_insult": 3,
                          "hits_threaten": 2, "hits_scream": 5},
        "q19c_gad2_participation": "answer",
        "q19c_gad2": {"gad2_item1": 1, "gad2_item2": 2},
        "q19d_cognition_selfreport": "no",
    }, section=19)
    assert scored.status_code == 200
    assert scored.json()["derived"] == {
        "phq2_score": 3, "depression_screen_positive": True,
        "hits_score": 11, "ipv_screen_positive": True,
        "gad2_score": 3, "anxiety_screen_positive": True,
    }


def test_zero_activity_days_does_not_require_minutes() -> None:
    response = validate(
        {"dem_age_group": "16_17", "q20a_pa_days": "0"}, section=20
    )
    assert response.status_code == 200
    assert response.json()["derived"]["weekly_minutes_activity"] == 0
    assert response.json()["derived"]["physical_activity_need"] is True


def test_activity_is_not_assessed_when_age_is_declined() -> None:
    response = validate({
        "dem_age_group": "prefer_not_answer", "q20a_pa_days": "3",
        "q20b_pa_minutes": 60,
    }, section=20)
    assert response.status_code == 200
    assert response.json()["derived"]["weekly_minutes_activity"] == 180
    assert response.json()["derived"]["physical_activity_need"] == "not_assessed"


def test_legal_other_domain_is_conditional_and_exclusive() -> None:
    missing = validate(
        {"legal_need": "not_sure", "legal_need_domains": ["other"]},
        section=21,
    )
    assert missing.status_code == 422
    assert "legal_need_other_text" in missing.json()["detail"]
    exclusive = validate({
        "legal_need": "not_sure",
        "legal_need_domains": ["housing_utilities", "prefer_not_answer"],
    }, section=21)
    assert exclusive.status_code == 422


def test_legal_support_result_identifies_access_barrier() -> None:
    response = validate({
        "legal_need": "yes", "legal_need_domains": ["housing_utilities"],
        "legal_support_access": "cost_or_access_barrier",
    }, section=21)
    assert response.status_code == 200
    assert response.json()["derived"]["potential_unmet_legal_need"] is True


def test_digital_access_section_requires_all_six_items() -> None:
    response = validate({"ddoh_device_access": "always"}, section=22)
    assert response.status_code == 422
    assert "ddoh_connectivity" in response.json()["detail"]
