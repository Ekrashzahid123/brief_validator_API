import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _APP_DIR.parent
for _d in (str(_PROJECT_DIR), str(_APP_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)

from fastapi import FastAPI, Header, status

try:
    from app.package_generator import generate_package
    from app.sample_data import SAMPLE_BRIEF_DATA
    from app.schemas import (
        HealthResponse,
        ProjectBrief,
        RootResponse,
        ValidationResponse,
    )
    from app.validator import validate_brief_and_package
except ImportError:
    from package_generator import generate_package
    from sample_data import SAMPLE_BRIEF_DATA
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
def get_sample() -> ProjectBrief:
    """
    Return a pre-configured synthetic sample project brief (VAL-001)
    ready for immediate validation testing.
    """
    return ProjectBrief(**SAMPLE_BRIEF_DATA)


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
