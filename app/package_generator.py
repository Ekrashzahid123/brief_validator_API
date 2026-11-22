import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _APP_DIR.parent
for _d in (str(_PROJECT_DIR), str(_APP_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)

try:
    from app.schemas import ProjectBrief, ProjectPackage
except ImportError:
    from schemas import ProjectBrief, ProjectPackage


def generate_package(brief: ProjectBrief, simulate_loss: bool = False) -> ProjectPackage:
    """
    Generates a structured ProjectPackage from an input ProjectBrief.
    
    Adheres strictly to the client's requirements without inventing or modifying
    any requirements or deliverables.

    Parameters:
    - brief: Validated ProjectBrief input.
    - simulate_loss: Optional flag to simulate package generation defect (omits a requirement)
      for deterministic testing of the validation failure workflow.
    """
    # Deterministic overview synthesized from title, client, and description
    project_overview = (
        f"{brief.project_title} for {brief.client_name}: {brief.project_description}"
    )

    # Requirements preserved faithfully unless simulated loss is triggered
    if simulate_loss and brief.requirements:
        requirements = list(brief.requirements[:-1])
    else:
        requirements = list(brief.requirements)

    # Scopes derived directly from explicit deliverables and functional requirements
    scope = (
        [f"Deliverable: {item}" for item in brief.deliverables]
        + [f"Functional Scope: {req}" for req in brief.requirements]
    )

    # Deterministic project execution assumptions
    assumptions = [
        "Client will provide timely access to necessary knowledge base source files and systems.",
        "Project delivery is bound strictly to the defined timeline and specified constraints.",
        "Scope additions outside listed deliverables require formal review and approval.",
    ]

    return ProjectPackage(
        project_overview=project_overview,
        objectives=list(brief.objectives),
        scope=scope,
        requirements=requirements,
        constraints=list(brief.constraints),
        deliverables=list(brief.deliverables),
        timeline=brief.timeline,
        budget=brief.budget,
        assumptions=assumptions,
    )
