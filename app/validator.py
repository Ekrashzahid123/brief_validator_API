import sys
from pathlib import Path
from typing import List, Tuple

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _APP_DIR.parent
for _d in (str(_PROJECT_DIR), str(_APP_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)

try:
    from app.schemas import (
        CheckItem,
        ProjectBrief,
        ProjectPackage,
        ValidationReport,
    )
except ImportError:
    from schemas import (
        CheckItem,
        ProjectBrief,
        ProjectPackage,
        ValidationReport,
    )


def validate_brief_and_package(
    brief: ProjectBrief, package: ProjectPackage
) -> Tuple[str, int, ValidationReport]:
    """
    Validates a generated ProjectPackage against its source ProjectBrief.

    Executes 8 core validation checks, calculates a percentage score,
    and returns (validation_status, score, ValidationReport).
    """
    checks: List[CheckItem] = []
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Required fields presence check
    required_brief_fields = {
        "case_id": brief.case_id,
        "client_name": brief.client_name,
        "project_title": brief.project_title,
        "project_description": brief.project_description,
        "timeline": brief.timeline,
    }
    missing_brief_fields = [k for k, v in required_brief_fields.items() if not str(v).strip()]
    package_has_overview = bool(package.project_overview and package.project_overview.strip())
    package_has_timeline = bool(package.timeline and package.timeline.strip())

    if not missing_brief_fields and package_has_overview and package_has_timeline:
        checks.append(CheckItem(
            name="required_fields_presence",
            passed=True,
            details="All required brief and package fields are present and non-empty."
        ))
    else:
        details = []
        if missing_brief_fields:
            details.append(f"Missing brief fields: {', '.join(missing_brief_fields)}")
        if not package_has_overview:
            details.append("Package is missing project_overview")
        if not package_has_timeline:
            details.append("Package is missing timeline")
        msg = "; ".join(details)
        errors.append(msg)
        checks.append(CheckItem(
            name="required_fields_presence",
            passed=False,
            details=msg
        ))

    # 2. Objectives not empty check
    if brief.objectives and package.objectives:
        checks.append(CheckItem(
            name="objectives_not_empty",
            passed=True,
            details=f"Brief has {len(brief.objectives)} objective(s); package has {len(package.objectives)}."
        ))
    else:
        msg = "Objectives cannot be empty in brief or generated package."
        errors.append(msg)
        checks.append(CheckItem(
            name="objectives_not_empty",
            passed=False,
            details=msg
        ))

    # 3. Requirements not empty check
    if brief.requirements and package.requirements:
        checks.append(CheckItem(
            name="requirements_not_empty",
            passed=True,
            details=f"Brief has {len(brief.requirements)} requirement(s); package has {len(package.requirements)}."
        ))
    else:
        msg = "Requirements cannot be empty in brief or generated package."
        errors.append(msg)
        checks.append(CheckItem(
            name="requirements_not_empty",
            passed=False,
            details=msg
        ))

    # 4. Deliverables not empty check
    if brief.deliverables and package.deliverables:
        checks.append(CheckItem(
            name="deliverables_not_empty",
            passed=True,
            details=f"Brief has {len(brief.deliverables)} deliverable(s); package has {len(package.deliverables)}."
        ))
    else:
        msg = "Deliverables cannot be empty in brief or generated package."
        errors.append(msg)
        checks.append(CheckItem(
            name="deliverables_not_empty",
            passed=False,
            details=msg
        ))

    # 5. All original requirements appear in the generated package
    brief_req_set = {r.strip() for r in brief.requirements}
    package_req_set = {r.strip() for r in package.requirements}
    missing_reqs = brief_req_set - package_req_set
    if not missing_reqs:
        checks.append(CheckItem(
            name="requirements_coverage",
            passed=True,
            details="All original requirements are retained in the generated package."
        ))
    else:
        msg = f"Requirements missing from generated package: {sorted(list(missing_reqs))}"
        errors.append(msg)
        checks.append(CheckItem(
            name="requirements_coverage",
            passed=False,
            details=msg
        ))

    # 6. All original deliverables appear in the generated package
    brief_deliv_set = {d.strip() for d in brief.deliverables}
    package_deliv_set = {d.strip() for d in package.deliverables}
    missing_delivs = brief_deliv_set - package_deliv_set
    if not missing_delivs:
        checks.append(CheckItem(
            name="deliverables_coverage",
            passed=True,
            details="All original deliverables are retained in the generated package."
        ))
    else:
        msg = f"Deliverables missing from generated package: {sorted(list(missing_delivs))}"
        errors.append(msg)
        checks.append(CheckItem(
            name="deliverables_coverage",
            passed=False,
            details=msg
        ))

    # 7. Project details consistency check (title, timeline, budget)
    details_mismatches = []
    if brief.project_title not in package.project_overview:
        details_mismatches.append("project_title not reflected in project_overview")
    if brief.timeline.strip() != package.timeline.strip():
        details_mismatches.append(f"timeline mismatch ('{brief.timeline}' vs '{package.timeline}')")
    if (brief.budget or "").strip() != (package.budget or "").strip():
        details_mismatches.append(f"budget mismatch ('{brief.budget}' vs '{package.budget}')")

    if not details_mismatches:
        checks.append(CheckItem(
            name="project_details_consistency",
            passed=True,
            details="Project title, timeline, and budget match between brief and package."
        ))
    else:
        msg = f"Project consistency discrepancies: {'; '.join(details_mismatches)}"
        errors.append(msg)
        checks.append(CheckItem(
            name="project_details_consistency",
            passed=False,
            details=msg
        ))

    # 8. No required information silently lost (objectives & constraints coverage)
    brief_obj_set = {o.strip() for o in brief.objectives}
    package_obj_set = {o.strip() for o in package.objectives}
    missing_objs = brief_obj_set - package_obj_set

    brief_const_set = {c.strip() for c in brief.constraints}
    package_const_set = {c.strip() for c in package.constraints}
    missing_consts = brief_const_set - package_const_set

    lost_info = []
    if missing_objs:
        lost_info.append(f"Lost objectives: {sorted(list(missing_objs))}")
    if missing_consts:
        lost_info.append(f"Lost constraints: {sorted(list(missing_consts))}")

    if not lost_info:
        checks.append(CheckItem(
            name="no_information_loss",
            passed=True,
            details="All objectives and constraints are completely preserved without loss."
        ))
    else:
        msg = "; ".join(lost_info)
        errors.append(msg)
        checks.append(CheckItem(
            name="no_information_loss",
            passed=False,
            details=msg
        ))

    # Non-critical warning checks
    if not brief.budget:
        warnings.append("Budget is unspecified in the project brief.")
    if not brief.constraints:
        warnings.append("No explicit constraints were defined in the project brief.")

    # Score calculation
    passed_count = sum(1 for c in checks if c.passed)
    total_count = len(checks)
    score = int(round((passed_count / total_count) * 100)) if total_count > 0 else 0

    validation_status = "PASS" if (len(errors) == 0 and score == 100) else "FAIL"

    report = ValidationReport(
        checks=checks,
        errors=errors,
        warnings=warnings
    )

    return validation_status, score, report
