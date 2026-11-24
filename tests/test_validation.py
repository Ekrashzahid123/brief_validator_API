import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.package_generator import generate_package
from app.sample_data import SAMPLE_BRIEF_DATA
from app.schemas import ProjectBrief, ProjectPackage
from app.validator import validate_brief_and_package

client = TestClient(app)


def test_health_endpoint():
    """7. Health endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Verify root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Brief-to-Package Validation API"
    assert data["status"] == "active"
    assert "version" in data


def test_sample_endpoint_returns_val_001():
    """8. Sample endpoint returns VAL-001."""
    response = client.get("/sample")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "VAL-001"
    assert data["client_name"] == "Demo Client"
    assert data["project_title"] == "AI Customer Support Assistant"
    assert len(data["requirements"]) > 0
    assert len(data["deliverables"]) > 0


def test_valid_brief_returns_pass():
    """1. Valid brief returns PASS with 100% score and clean report."""
    response = client.post("/validate", json=SAMPLE_BRIEF_DATA)
    assert response.status_code == 200
    data = response.json()

    assert data["case_id"] == "VAL-001"
    assert data["validation_status"] == "PASS"
    assert data["score"] == 100

    report = data["validation_report"]
    assert len(report["errors"]) == 0
    assert all(c["passed"] for c in report["checks"])

    package = data["generated_package"]
    assert "AI Customer Support Assistant" in package["project_overview"]
    assert len(package["requirements"]) == len(SAMPLE_BRIEF_DATA["requirements"])
    assert len(package["deliverables"]) == len(SAMPLE_BRIEF_DATA["deliverables"])


def test_missing_project_title_rejected():
    """2. Missing project title is rejected with HTTP 422."""
    payload = SAMPLE_BRIEF_DATA.copy()
    payload.pop("project_title")

    response = client.post("/validate", json=payload)
    assert response.status_code == 422

    # Also test empty string for project_title
    payload_empty_title = SAMPLE_BRIEF_DATA.copy()
    payload_empty_title["project_title"] = "   "
    response_empty = client.post("/validate", json=payload_empty_title)
    assert response_empty.status_code == 422


def test_empty_requirements_detected():
    """3. Empty requirements are detected and rejected with HTTP 422."""
    payload = SAMPLE_BRIEF_DATA.copy()
    payload["requirements"] = []

    response = client.post("/validate", json=payload)
    assert response.status_code == 422

    # Also test list containing only whitespace
    payload_whitespace = SAMPLE_BRIEF_DATA.copy()
    payload_whitespace["requirements"] = ["   ", ""]
    response_ws = client.post("/validate", json=payload_whitespace)
    assert response_ws.status_code == 422


def test_missing_deliverables_detected():
    """4. Missing deliverables are detected and rejected with HTTP 422."""
    payload = SAMPLE_BRIEF_DATA.copy()
    payload.pop("deliverables")

    response = client.post("/validate", json=payload)
    assert response.status_code == 422

    # Also test empty deliverables list
    payload_empty_deliv = SAMPLE_BRIEF_DATA.copy()
    payload_empty_deliv["deliverables"] = []
    response_empty = client.post("/validate", json=payload_empty_deliv)
    assert response_empty.status_code == 422


def test_requirements_missing_from_generated_package_causes_fail():
    """5. Requirements missing from the generated package cause FAIL."""
    brief = ProjectBrief(**SAMPLE_BRIEF_DATA)
    # Generate package normally
    package = generate_package(brief)

    # Intentionally remove one requirement from the generated package
    tampered_requirements = package.requirements[:-1]
    tampered_package = ProjectPackage(
        project_overview=package.project_overview,
        objectives=package.objectives,
        scope=package.scope,
        requirements=tampered_requirements,
        constraints=package.constraints,
        deliverables=package.deliverables,
        timeline=package.timeline,
        budget=package.budget,
        assumptions=package.assumptions,
    )

    status, score, report = validate_brief_and_package(brief, tampered_package)

    assert status == "FAIL"
    assert score < 100
    assert any("Requirements missing" in err for err in report.errors)
    # Check that requirements_coverage check failed
    coverage_check = next(c for c in report.checks if c.name == "requirements_coverage")
    assert coverage_check.passed is False


def test_deliverables_missing_from_generated_package_causes_fail():
    """Validation fails if deliverables are omitted from the generated package."""
    brief = ProjectBrief(**SAMPLE_BRIEF_DATA)
    package = generate_package(brief)

    # Remove a deliverable
    tampered_package = ProjectPackage(
        project_overview=package.project_overview,
        objectives=package.objectives,
        scope=package.scope,
        requirements=package.requirements,
        constraints=package.constraints,
        deliverables=package.deliverables[:-1],
        timeline=package.timeline,
        budget=package.budget,
        assumptions=package.assumptions,
    )

    status, score, report = validate_brief_and_package(brief, tampered_package)
    assert status == "FAIL"
    assert any("Deliverables missing" in err for err in report.errors)


def test_api_with_simulated_loss_returns_fail():
    """Verify POST /validate with X-Simulate-Loss header returns FAIL via API."""
    response = client.post(
        "/validate",
        json=SAMPLE_BRIEF_DATA,
        headers={"x-simulate-loss": "true"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["validation_status"] == "FAIL"
    assert data["score"] < 100
    assert len(data["validation_report"]["errors"]) > 0
    assert any("Requirements missing" in err for err in data["validation_report"]["errors"])


def test_score_calculation_works_correctly():
    """6. Score calculation works correctly across pass, partial, and full failures."""
    brief = ProjectBrief(**SAMPLE_BRIEF_DATA)
    package = generate_package(brief)

    # 100% Score when clean
    status, score, report = validate_brief_and_package(brief, package)
    assert score == 100
    assert status == "PASS"

    # Single failure: change timeline
    mismatched_package = ProjectPackage(
        project_overview=package.project_overview,
        objectives=package.objectives,
        scope=package.scope,
        requirements=package.requirements,
        constraints=package.constraints,
        deliverables=package.deliverables,
        timeline="10 weeks",  # mismatched
        budget=package.budget,
        assumptions=package.assumptions,
    )
    status_mismatch, score_mismatch, report_mismatch = validate_brief_and_package(brief, mismatched_package)
    assert status_mismatch == "FAIL"
    # 7 out of 8 checks pass = 88%
    assert score_mismatch == round((7 / 8) * 100)
    assert score_mismatch == 88


def test_warning_generation_on_missing_optional_fields():
    """Verify warnings are produced when optional fields like budget are omitted."""
    data = SAMPLE_BRIEF_DATA.copy()
    data["budget"] = None
    data["constraints"] = []

    brief = ProjectBrief(**data)
    package = generate_package(brief)
    status, score, report = validate_brief_and_package(brief, package)

    assert status == "PASS"
    assert score == 100
    assert any("Budget is unspecified" in w for w in report.warnings)
    assert any("No explicit constraints" in w for w in report.warnings)


def test_list_all_samples_endpoint():
    """Verify GET /samples returns all 4 sample briefs."""
    response = client.get("/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) == 4
    case_ids = [s["case_id"] for s in samples]
    assert case_ids == ["VAL-001", "VAL-002", "VAL-003", "VAL-004"]


@pytest.mark.parametrize("case_id", ["VAL-001", "VAL-002", "VAL-003", "VAL-004"])
def test_all_sample_cases_validate_successfully(case_id):
    """Verify all 4 sample cases return PASS and score 100 on /validate."""
    sample_resp = client.get(f"/sample?case_id={case_id}")
    assert sample_resp.status_code == 200
    brief_data = sample_resp.json()
    assert brief_data["case_id"] == case_id

    validate_resp = client.post("/validate", json=brief_data)
    assert validate_resp.status_code == 200
    res = validate_resp.json()
    assert res["validation_status"] == "PASS"
    assert res["score"] == 100
    assert len(res["validation_report"]["errors"]) == 0


def test_sample_not_found():
    """Verify requesting an invalid sample case returns HTTP 404."""
    response = client.get("/sample?case_id=VAL-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
