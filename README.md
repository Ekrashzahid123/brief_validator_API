# Brief-to-Package Validation API

A clean, production-grade, deterministic validation prototype built with **FastAPI** and **Pydantic v2**.

This API takes an incoming client project brief, validates its structural requirements, deterministically generates a formal project package, and verifies whether the generated package strictly and consistently fulfills the original brief without omitting requirements or inventing unauthorized scope.

---

## Tech Stack
- **Python**: 3.11+ (Tested on Python 3.12)
- **Framework**: FastAPI
- **Validation & Serialization**: Pydantic v2
- **ASGI Server**: Uvicorn
- **Testing**: Pytest & HTTPX (TestClient)

---

## Project Structure

```text
brief_validator/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI application and endpoint definitions
│   ├── schemas.py            # Pydantic v2 data models with field validations
│   ├── validator.py          # Deterministic 8-point validation engine & scoring
│   ├── package_generator.py  # Deterministic package synthesis from brief
│   └── sample_data.py        # Synthetic test case (VAL-001)
├── tests/
│   ├── __init__.py
│   └── test_validation.py    # Pytest test suite covering all requirements
├── requirements.txt
└── README.md
```

---

## Core Workflow & Validation Checks

1. **Input Schema Validation**: Pydantic validates non-empty fields, required string contents, and non-empty arrays.
2. **Package Generation**: Derives `project_overview`, `objectives`, `scope`, `requirements`, `constraints`, `deliverables`, `timeline`, `budget`, and baseline `assumptions`.
3. **8-Point Deterministic Engine Checks**:
   - `required_fields_presence`: All critical brief and package fields are present and populated.
   - `objectives_not_empty`: Objectives list contains at least one valid item.
   - `requirements_not_empty`: Functional requirements list is populated.
   - `deliverables_not_empty`: Deliverables list is populated.
   - `requirements_coverage`: Every requirement from the original brief appears in the package.
   - `deliverables_coverage`: Every deliverable from the original brief appears in the package.
   - `project_details_consistency`: Title, timeline, and budget match between brief and package.
   - `no_information_loss`: Constraints and objectives are preserved without silent loss.

---

## Installation & Setup

1. **Clone / Navigate to Project Directory**:
   ```bash
   cd brief_validator
   ```

2. **Create and Activate a Virtual Environment** *(recommended)*:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the API Server

Start the Uvicorn ASGI server with live reloading:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## Running Automated Tests

Run the complete test suite with Pytest:

```bash
# From within the brief_validator directory:
pytest -v

# Or from the project root:
pytest brief_validator -v
```

All 12 test scenarios will execute, verifying:
- Valid brief returns `PASS` and score 100
- Missing or empty `project_title` is rejected with HTTP 422
- Empty `requirements` list is rejected with HTTP 422
- Missing or empty `deliverables` are rejected with HTTP 422
- Omitted requirement from generated package causes `FAIL`
- Score calculation accurately calculates passing percentage
- `/health` and `/sample` endpoints function correctly
- `X-Simulate-Loss` debugging header triggers validation `FAIL`

---

## Interactive Testing via Swagger UI

1. Open `http://127.0.0.1:8000/docs` in your browser.
2. **Explore Sample Briefs**:
   - `GET /sample`: Returns default sample `VAL-001`. You can pass `case_id` query parameter (`VAL-001`, `VAL-002`, `VAL-003`, `VAL-004`).
   - `GET /samples`: Returns all 4 synthetic sample briefs across different industry domains.
3. **Synthetic Sample Library**:
   - `VAL-001`: **AI Customer Support Assistant** (Knowledge Base RAG, $5,000, 4 weeks)
   - `VAL-002`: **Intelligent Invoice Extraction & Reconciliation System** (FinTech OCR & ERP matching, $12,000, 6 weeks)
   - `VAL-003`: **E-Commerce Real-Time Personalization & Search Engine** (Retail vector search & ranking, $18,000, 8 weeks)
   - `VAL-004`: **Clinical Note Summarization & Triage Assistant** (Healthcare NLP & FHIR compliance, $25,000, 10 weeks)
4. Expand `POST /validate` and click **Try it out**.
5. Paste any of the sample brief JSON objects into the Request Body and click **Execute**.
6. Observe the generated package, score `100`, and `PASS` status.
7. To test a failure scenario:
   - Provide an empty string for `"project_title": ""` to see HTTP 422 schema validation error.
   - Or set the header `x-simulate-loss: true` to observe the validation engine detect a missing requirement and return status `FAIL` with a reduced score.

---

## API Examples

### 1. Successful Validation (PASS)

**Request**: `POST /validate`
```json
{
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
```

**Response**: `HTTP 200 OK`
```json
{
  "case_id": "VAL-001",
  "validation_status": "PASS",
  "score": 100,
  "generated_package": {
    "project_overview": "AI Customer Support Assistant for Demo Client: Build an AI-powered support assistant that answers customer questions using company knowledge base documents.",
    "objectives": [
      "Answer customer queries using company documentation.",
      "Reduce repetitive customer support workload.",
      "Provide relevant answers based on available information."
    ],
    "scope": [
      "Deliverable: Project brief.",
      "Deliverable: Technical scope.",
      "Deliverable: System architecture.",
      "Deliverable: Implementation plan.",
      "Deliverable: Validation report.",
      "Functional Scope: Document-based question answering.",
      "Functional Scope: Knowledge base ingestion.",
      "Functional Scope: Search relevant documents.",
      "Functional Scope: Provide answers with source references."
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
    "budget": "$5,000",
    "assumptions": [
      "Client will provide timely access to necessary knowledge base source files and systems.",
      "Project delivery is bound strictly to the defined timeline and specified constraints.",
      "Scope additions outside listed deliverables require formal review and approval."
    ]
  },
  "validation_report": {
    "checks": [
      {
        "name": "required_fields_presence",
        "passed": true,
        "details": "All required brief and package fields are present and non-empty."
      },
      {
        "name": "objectives_not_empty",
        "passed": true,
        "details": "Brief has 3 objective(s); package has 3."
      },
      {
        "name": "requirements_not_empty",
        "passed": true,
        "details": "Brief has 4 requirement(s); package has 4."
      },
      {
        "name": "deliverables_not_empty",
        "passed": true,
        "details": "Brief has 5 deliverable(s); package has 5."
      },
      {
        "name": "requirements_coverage",
        "passed": true,
        "details": "All original requirements are retained in the generated package."
      },
      {
        "name": "deliverables_coverage",
        "passed": true,
        "details": "All original deliverables are retained in the generated package."
      },
      {
        "name": "project_details_consistency",
        "passed": true,
        "details": "Project title, timeline, and budget match between brief and package."
      },
      {
        "name": "no_information_loss",
        "passed": true,
        "details": "All objectives and constraints are completely preserved without loss."
      }
    ],
    "errors": [],
    "warnings": []
  }
}
```

---

### 2. Failed Validation Examples

#### A. Schema Rejection (Empty Requirements)
**Request**: `POST /validate` with `"requirements": []`

**Response**: `HTTP 422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "requirements"
      ],
      "msg": "Value error, requirements must contain at least one non-empty string.",
      "input": []
    }
  ]
}
```

#### B. Engine Validation Failure (Requirement Missing from Package)
**Request**: `POST /validate` with header `x-simulate-loss: true`

**Response**: `HTTP 200 OK`
```json
{
  "case_id": "VAL-001",
  "validation_status": "FAIL",
  "score": 88,
  "generated_package": { ... },
  "validation_report": {
    "checks": [
      ...
      {
        "name": "requirements_coverage",
        "passed": false,
        "details": "Requirements missing from generated package: ['Provide answers with source references.']"
      },
      ...
    ],
    "errors": [
      "Requirements missing from generated package: ['Provide answers with source references.']"
    ],
    "warnings": []
  }
}
```
