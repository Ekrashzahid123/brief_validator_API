import sys
from pathlib import Path
from typing import Any, Dict, List

_APP_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _APP_DIR.parent
for _d in (str(_PROJECT_DIR), str(_APP_DIR)):
    if _d not in sys.path:
        sys.path.insert(0, _d)

try:
    from app.schemas import ProjectBrief
except ImportError:
    from schemas import ProjectBrief

SAMPLE_CASES: Dict[str, Dict[str, Any]] = {
    "VAL-001": {
        "case_id": "VAL-001",
        "client_name": "Demo Client",
        "project_title": "AI Customer Support Assistant",
        "project_description": "Build an AI-powered support assistant that answers customer questions using company knowledge base documents.",
        "objectives": [
            "Answer customer queries using company documentation.",
            "Reduce repetitive customer support workload.",
            "Provide relevant answers based on available information.",
            "Achieve sub-2-second response latency for document queries.",
            "Log unanswerable queries for documentation gap analysis."
        ],
        "requirements": [
            "Document-based question answering.",
            "Knowledge base ingestion.",
            "Search relevant documents.",
            "Provide answers with source references.",
            "Role-based access control for administrative document uploads.",
            "Feedback rating mechanism for generated support responses."
        ],
        "constraints": [
            "Do not invent information outside the supplied documentation.",
            "If the answer is not found, the assistant must indicate insufficient information.",
            "Only PDF and TXT files are supported in the prototype.",
            "Max file upload size is capped at 25MB per document."
        ],
        "deliverables": [
            "Project brief.",
            "Technical scope.",
            "System architecture.",
            "Implementation plan.",
            "Validation report.",
            "API documentation and Postman collection.",
            "Automated test coverage report."
        ],
        "timeline": "4 weeks",
        "budget": "$5,000"
    },
    "VAL-002": {
        "case_id": "VAL-002",
        "client_name": "FinTech Global Ltd",
        "project_title": "Intelligent Invoice Extraction & Reconciliation System",
        "project_description": "Automated OCR and parsing pipeline to extract vendor metadata, line items, taxes, and payment totals from scanned invoices, cross-referencing against internal ERP purchase orders.",
        "objectives": [
            "Automate extraction of structured invoice data from scanned PDFs and images.",
            "Reconcile extracted invoice line items against ERP purchase orders.",
            "Flag discrepancies and invoice anomalies above a 2% variance threshold.",
            "Reduce manual accounting processing cycle from 3 days to under 15 minutes."
        ],
        "requirements": [
            "Multi-page PDF and TIFF document parsing.",
            "Line-item extraction including SKU, description, unit price, quantity, and total.",
            "Automated tax and subtotal mathematical verification.",
            "ERP reconciliation matching engine via REST webhook.",
            "Human-in-the-loop review portal for flagged discrepancies."
        ],
        "constraints": [
            "Compliance with SOC2 and GDPR document retention regulations.",
            "Strict PII masking on vendor bank details before analytics ingestion.",
            "Process invoices with minimum 98% line-item field precision."
        ],
        "deliverables": [
            "Document ingestion and OCR parser microservice.",
            "Reconciliation and anomaly detection engine.",
            "PostgreSQL database migration scripts for audit trail.",
            "Discrepancy review interface.",
            "Deployment runbook and CI/CD pipeline definition."
        ],
        "timeline": "6 weeks",
        "budget": "$12,000"
    },
    "VAL-003": {
        "case_id": "VAL-003",
        "client_name": "Apex Retailers Inc.",
        "project_title": "E-Commerce Real-Time Personalization & Search Engine",
        "project_description": "Build an intelligent search and recommendation engine providing real-time product discovery, semantic search queries, and personalized cross-selling based on user session behavior.",
        "objectives": [
            "Deliver sub-100ms semantic search across a catalog of 200,000 SKUs.",
            "Increase average order value by 12% through personalized product bundles.",
            "Handle search queries with typos, synonyms, and natural language phrasing."
        ],
        "requirements": [
            "Vector embedding generation and semantic similarity indexing.",
            "Faceted category filtering by price, brand, rating, and availability.",
            "Real-time session clickstream analytics collector.",
            "Collaborative and content-based recommendation hybrid algorithm.",
            "A/B testing experimentation framework for search ranking weights."
        ],
        "constraints": [
            "Peak throughput must sustain at least 2,500 queries per second.",
            "Zero external cloud dependencies for raw customer payment telemetry.",
            "Cache hit ratio must exceed 85% for top 1,000 frequent search queries."
        ],
        "deliverables": [
            "Semantic search API microservice.",
            "Recommendation model training and inference pipelines.",
            "Catalog indexing and synchronization batch worker.",
            "Load testing benchmark report.",
            "Integration SDK for web and mobile storefronts."
        ],
        "timeline": "8 weeks",
        "budget": "$18,000"
    },
    "VAL-004": {
        "case_id": "VAL-004",
        "client_name": "CarePoint Health Network",
        "project_title": "Clinical Note Summarization & Triage Assistant",
        "project_description": "Secure clinical text processing solution that transcribes and condenses patient intake notes, structures clinical findings into SOAP notes, and alerts attending physicians of critical vitals.",
        "objectives": [
            "Convert unstructured clinician dictated notes into standardized SOAP notes.",
            "Extract primary symptoms, past medical history, and prescribed medications.",
            "Highlight urgent clinical red flags and abnormal vital sign indicators.",
            "Reduce clinician administrative documentation burden by 40%."
        ],
        "requirements": [
            "Medical terminology entity extraction using standard SNOMED-CT / ICD-10 codes.",
            "Structured SOAP (Subjective, Objective, Assessment, Plan) format generation.",
            "Immediate push notifications for vital sign emergency thresholds.",
            "HL7 FHIR compliant data export connector for EHR integration."
        ],
        "constraints": [
            "Strict HIPAA compliance; all data must be encrypted in transit (TLS 1.3) and at rest (AES-256).",
            "Zero retention of raw patient voice audio once note is confirmed.",
            "Audit logging of every physician view and note edit."
        ],
        "deliverables": [
            "Clinical NLP processing engine.",
            "FHIR interoperability gateway.",
            "Physician web review and sign-off portal.",
            "HIPAA compliance audit and security vulnerability scan report.",
            "User training guide and administrator manual."
        ],
        "timeline": "10 weeks",
        "budget": "$25,000"
    }
}

# Default sample data for backwards compatibility
SAMPLE_BRIEF_DATA: Dict[str, Any] = SAMPLE_CASES["VAL-001"]


def get_sample_brief(case_id: str = "VAL-001") -> ProjectBrief:
    """Returns a validated ProjectBrief instance for the requested case_id."""
    data = SAMPLE_CASES.get(case_id, SAMPLE_BRIEF_DATA)
    return ProjectBrief(**data)


def get_all_sample_briefs() -> List[ProjectBrief]:
    """Returns a list of all pre-configured synthetic sample briefs."""
    return [ProjectBrief(**data) for data in SAMPLE_CASES.values()]
