import sys
from pathlib import Path
from typing import List, Optional

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _APP_DIR.parent
for _d in (str(_PROJECT_DIR), str(_APP_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectBrief(BaseModel):
    """Input project brief schema with strict validations."""
    model_config = ConfigDict(str_strip_whitespace=True)

    case_id: str = Field(..., description="Unique case identifier", min_length=1)
    client_name: str = Field(..., description="Client name", min_length=1)
    project_title: str = Field(..., description="Title of the project", min_length=1)
    project_description: str = Field(..., description="Detailed description of project", min_length=1)
    objectives: List[str] = Field(..., description="List of primary project objectives", min_length=1)
    requirements: List[str] = Field(..., description="List of functional/project requirements", min_length=1)
    constraints: List[str] = Field(default_factory=list, description="List of project constraints")
    deliverables: List[str] = Field(..., description="List of agreed deliverables", min_length=1)
    timeline: str = Field(..., description="Estimated project duration or milestone timeline", min_length=1)
    budget: Optional[str] = Field(default=None, description="Project budget, if specified")

    @field_validator("objectives", "requirements", "deliverables")
    @classmethod
    def validate_non_empty_items(cls, items: List[str], info) -> List[str]:
        cleaned = [item.strip() for item in items if item and item.strip()]
        if not cleaned:
            raise ValueError(f"{info.field_name} must contain at least one non-empty string.")
        return cleaned

    @field_validator("constraints")
    @classmethod
    def validate_constraints_items(cls, items: List[str]) -> List[str]:
        return [item.strip() for item in items if item and item.strip()]


class ProjectPackage(BaseModel):
    """Generated structured project package."""
    model_config = ConfigDict(str_strip_whitespace=True)

    project_overview: str
    objectives: List[str]
    scope: List[str]
    requirements: List[str]
    constraints: List[str]
    deliverables: List[str]
    timeline: str
    budget: Optional[str] = None
    assumptions: List[str]


class CheckItem(BaseModel):
    """Result of an individual validation check."""
    name: str
    passed: bool
    details: str


class ValidationReport(BaseModel):
    """Validation report containing checks, errors, and warnings."""
    checks: List[CheckItem]
    errors: List[str]
    warnings: List[str]


class ValidationResponse(BaseModel):
    """Complete response returned by POST /validate."""
    case_id: str
    validation_status: str
    score: int
    generated_package: ProjectPackage
    validation_report: ValidationReport


class RootResponse(BaseModel):
    name: str
    version: str
    status: str


class HealthResponse(BaseModel):
    status: str
