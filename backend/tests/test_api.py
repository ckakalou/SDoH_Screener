from fastapi.testclient import TestClient

from backend.app.main import app, calculate_derived_results


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
    assert "q19e_mmse_total" not in ids
    hits = next(q for q in screener["questions"] if q["id"] == "q19b_ipv_hits")
    assert "visible_if" not in hits


def test_all_questions_have_explicit_required_metadata() -> None:
    questions = client.get("/api/v1/screener").json()["screener"]["questions"]
    assert all("required" in question for question in questions)
    assert {q["id"] for q in questions if q["required"] is False} == {
        "dem_gender", "q1_ethnic_group", "q2_ancestry",
        "q9b_longest_zip",
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
        "q19b_ipv_hits": {"hits_hurt": 1, "hits_insult": 1,
                          "hits_threaten": 1, "hits_scream": 1},
        "q19c_gad2_participation": "decline",
        "q19d_cognition_selfreport": "no",
    }, section=19)
    assert declined.status_code == 200
    derived = declined.json()["derived"]
    assert derived["screening_results"]["depression"]["assessment_status"] == "declined"
    assert derived["restricted_safety_indicators"]["ipv"]["score"] == 4

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
    derived = scored.json()["derived"]
    assert derived["screening_results"] == {
        "depression": {
            "assessment_status": "assessed", "instrument": "phq_2",
            "score": 3, "screen_positive": True,
        },
        "anxiety": {
            "assessment_status": "assessed", "instrument": "gad_2",
            "score": 3, "screen_positive": True,
        },
    }
    assert derived["restricted_safety_indicators"]["ipv"] == {
        "assessment_status": "assessed", "instrument": "hits",
        "score": 11, "screen_positive": True,
    }


def test_zero_activity_days_does_not_require_minutes() -> None:
    response = validate(
        {"dem_age_group": "16_17", "q20a_pa_days": "0"}, section=20
    )
    assert response.status_code == 200
    activity = response.json()["derived"]["needs"]["physical_activity"]
    assert activity["weekly_minutes"] == 0
    assert activity["need_identified"] is True


def test_positive_activity_days_do_not_accept_zero_minutes() -> None:
    response = validate({
        "dem_age_group": "22_30", "q20a_pa_days": "1",
        "q20b_pa_minutes": 0,
    }, section=20)
    assert response.status_code == 422


def test_activity_is_not_assessed_when_age_is_declined() -> None:
    response = validate({
        "dem_age_group": "prefer_not_answer", "q20a_pa_days": "3",
        "q20b_pa_minutes": 60,
    }, section=20)
    assert response.status_code == 200
    activity = response.json()["derived"]["needs"]["physical_activity"]
    assert activity == {
        "assessment_status": "not_assessed",
        "weekly_minutes": 180,
        "need_identified": None,
    }


def test_transportation_domains_are_distinct_and_exclusive() -> None:
    assessed = validate({
        "q15a_commute_mode": "bus_coach_minibus",
        "q15b_transport_barrier": ["healthcare"],
    }, section=15)
    assert assessed.status_code == 200
    derived = assessed.json()["derived"]
    assert derived["context"]["transportation"]["usual_travel_mode"] == (
        "bus_coach_minibus"
    )
    assert derived["needs"]["transportation"] == {
        "assessment_status": "assessed",
        "barrier_reported": True,
        "healthcare_access_affected": True,
        "daily_living_access_affected": False,
    }

    invalid = validate({
        "q15a_commute_mode": "walked",
        "q15b_transport_barrier": ["none", "daily_living"],
    }, section=15)
    assert invalid.status_code == 422


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
    legal = response.json()["derived"]["needs"]["legal_support"]
    assert legal == {
        "assessment_status": "assessed",
        "domains": ["housing_utilities"],
        "unmet_need_identified": True,
    }


def test_uncertain_legal_need_is_not_converted_to_false() -> None:
    response = validate({
        "legal_need": "not_sure",
        "legal_need_domains": ["housing_utilities"],
    }, section=21)
    assert response.status_code == 200
    legal = response.json()["derived"]["needs"]["legal_support"]
    assert legal["assessment_status"] == "uncertain"
    assert legal["unmet_need_identified"] is None


def test_digital_access_section_requires_all_six_items() -> None:
    response = validate({"ddoh_device_access": "always"}, section=22)
    assert response.status_code == 422
    assert "ddoh_connectivity" in response.json()["detail"]


def test_digital_barriers_and_combined_internet_access_are_derived() -> None:
    response = validate({
        "q11_internet": True,
        "ddoh_device_access": "sometimes",
        "ddoh_connectivity": "sometimes",
        "ddoh_affordability": "no",
        "ddoh_accessibility": "never",
        "ddoh_support": "no_assistance_needed",
        "ddoh_privacy_trust": "yes",
    }, section=22)
    assert response.status_code == 200
    derived = response.json()["derived"]
    assert derived["context"]["digital_connectivity"] == {
        "assessment_status": "assessed",
        "household_home_internet": True,
        "household_home_internet_status": "assessed",
        "personal_connectivity": "sometimes",
        "internet_access_level": "intermittent_despite_home_access",
    }
    assert derived["needs"]["digital_access"] == {
        "device_access_barrier": True,
        "connectivity_barrier": True,
        "affordability_barrier": False,
        "accessibility_barrier": True,
        "support_barrier": False,
        "privacy_trust_barrier": True,
    }


def test_four_tier_contract_retains_approved_context_without_free_text_other() -> None:
    derived = calculate_derived_results({
        "dem_age_group": "71_80",
        "dem_gender": "another_gender",
        "dem_gender_other_text": "not exported",
        "q1_ethnic_group": ["white", "other"],
        "q1_ethnic_group_other_text": "not exported",
        "q2_europe_region": "southern_europe",
        "q2_ancestry": "Greek",
        "q3_household_income": "20000_29999",
        "q4_education": "masters",
        "q5_work_status": "unemployed",
        "q5b_last_worked": "one_to_five_years",
        "q9b_longest_zip": "54622",
        "q14a_marital_status": "divorced",
        "q14b_single_parent": True,
        "q15a_commute_mode": "bus_coach_minibus",
    })
    assert set(derived) == {
        "schema_version", "context", "needs", "screening_results",
        "restricted_safety_indicators",
    }
    assert derived["context"]["economic"]["household_income_band"] == (
        "20000_29999"
    )
    assert derived["context"]["identity"]["ancestry"]["reported_value"] == "Greek"
    assert derived["context"]["geographic_linkage"]["postal_code"] == "54622"
    assert derived["context"]["family"]["marital_status"] == "divorced"
    assert derived["context"]["transportation"]["usual_travel_mode"] == (
        "bus_coach_minibus"
    )
    serialized = str(derived)
    assert "not exported" not in serialized
    assert "threshold" not in serialized
