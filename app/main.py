import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _APP_DIR.parent
for _d in (str(_PROJECT_DIR), str(_APP_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)

from typing import List
from fastapi import FastAPI, Header, HTTPException, Query, status

try:
    from app.package_generator import generate_package
    from app.sample_data import (
        SAMPLE_BRIEF_DATA,
        SAMPLE_CASES,
        get_all_sample_briefs,
        get_sample_brief,
    )
    from app.schemas import (
        HealthResponse,
        ProjectBrief,
        RootResponse,
        ValidationResponse,
    )
    from app.validator import validate_brief_and_package
except ImportError:
    from package_generator import generate_package
    from sample_data import (
        SAMPLE_BRIEF_DATA,
        SAMPLE_CASES,
        get_all_sample_briefs,
        get_sample_brief,
    )
    from schemas import (
        HealthResponse,
        ProjectBrief,
        RootResponse,
        ValidationResponse,
    )
    from validator import validate_brief_and_package

app = FastAPI(
    title="Brief-to-Package Validation API",
    version="1.0.0",
    description="A deterministic validation engine that receives project briefs, generates structured packages, and verifies consistency.",
)


@app.get(
    "/",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    summary="API Info and Status",
)
def read_root() -> RootResponse:
    """Return API metadata, version, and running status."""
    return RootResponse(
        name="Brief-to-Package Validation API",
        version="1.0.0",
        status="active",
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
)
def health_check() -> HealthResponse:
    """Return system health status."""
    return HealthResponse(status="healthy")


@app.get(
    "/sample",
    response_model=ProjectBrief,
    status_code=status.HTTP_200_OK,
    summary="Get Synthetic Sample Brief",
)
def get_sample(
    case_id: str = Query(
        default="VAL-001",
        description="Case ID of the synthetic sample brief (VAL-001, VAL-002, VAL-003, VAL-004)",
    )
) -> ProjectBrief:
    """
    Return a pre-configured synthetic sample project brief ready for validation testing.
    Defaults to VAL-001. Other available cases: VAL-002, VAL-003, VAL-004.
    """
    if case_id not in SAMPLE_CASES:
        available = list(SAMPLE_CASES.keys())
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample case '{case_id}' not found. Available cases: {available}",
        )
    return get_sample_brief(case_id)


@app.get(
    "/samples",
    response_model=List[ProjectBrief],
    status_code=status.HTTP_200_OK,
    summary="List All Synthetic Sample Briefs",
)
def get_all_samples() -> List[ProjectBrief]:
    """Return all available pre-configured synthetic sample project briefs."""
    return get_all_sample_briefs()


@app.post(
    "/validate",
    response_model=ValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate Brief & Generate Package",
)
def validate_brief(
    brief: ProjectBrief,
    x_simulate_loss: bool = Header(
        default=False,
        description="Optional test header: simulate omission of a requirement in generated package to inspect FAIL result",
    ),
) -> ValidationResponse:
    """
    Accepts a project brief, generates a structured project package,
    and runs deterministic validation checks comparing the brief to the package.
    """
    # 1. Input schema is automatically validated via FastAPI & Pydantic
    # 2. Generate structured project package
    package = generate_package(brief, simulate_loss=x_simulate_loss)

    # 3. Execute validation engine checks
    validation_status, score, report = validate_brief_and_package(brief, package)

    # 4. Construct and return response
    return ValidationResponse(
        case_id=brief.case_id,
        validation_status=validation_status,
        score=score,
        generated_package=package,
        validation_report=report,
    )
