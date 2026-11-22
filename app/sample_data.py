import sys
from pathlib import Path
from typing import Any, Dict

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _APP_DIR.parent
for _d in (str(_PROJECT_DIR), str(_APP_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)

try:
    from app.schemas import ProjectBrief
except ImportError:
    from schemas import ProjectBrief

SAMPLE_BRIEF_DATA: Dict[str, Any] = {
    "case_id": "VAL-001",
    "client_name": "Demo Client",
    "project_title": "AI Customer Support Assistant",
    "project_description": "Build an AI-powered support assistant that answers customer questions using company knowledge base documents.",
    "objectives": [
        "Answer customer queries using company documentation.",
        "Reduce repetitive customer support workload.",
        "Provide relevant answers based on available information."
    ],
    "requirements": [
        "Document-based question answering.",
        "Knowledge base ingestion.",
        "Search relevant documents.",
        "Provide answers with source references."
    ],
    "constraints": [
        "Do not invent information outside the supplied documentation.",
        "If the answer is not found, the assistant must indicate insufficient information.",
        "Only PDF and TXT files are supported in the prototype."
    ],
    "deliverables": [
        "Project brief.",
        "Technical scope.",
        "System architecture.",
        "Implementation plan.",
        "Validation report."
    ],
    "timeline": "4 weeks",
    "budget": "$5,000"
}


def get_sample_brief() -> ProjectBrief:
    """Returns a validated ProjectBrief instance initialized with sample data."""
    return ProjectBrief(**SAMPLE_BRIEF_DATA)
