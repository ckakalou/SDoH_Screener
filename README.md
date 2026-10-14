---
title: HEALIE SD-DOH Assessment
emoji: 🪼
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
---

# HEALIE SD-DOH Assessment

A schema-driven **Social and Digital Determinants of Health (SD-DOH)** assessment developed as part of the HEALIE research project. The participant-facing title is **Social and Digital Factors Affecting Health**.

The current redesign uses:

- React and TypeScript for the frontend
- FastAPI for the backend API
- JSON Schema for response validation
- An EU/Greek-adapted questionnaire definition with separately documented legal-needs and digital-access modules

> Research software under active development. It is not currently intended for clinical use.

## Current functionality

The React/FastAPI implementation currently supports:

- Loading the questionnaire definition from FastAPI
- Rendering questions dynamically from the EU/GR v2 JSON configuration
- Section-by-section navigation with progress feedback
- Shared answer state across all sections
- Conditional visibility using `any` and `all` rules
- Equality and multi-select containment conditions
- Automatic removal of answers when conditional questions become hidden
- Required-question checks before moving to the next section
- Explicit optional-question metadata and exclusive decline choices
- Submission of answers to FastAPI
- Server-side validation using JSON Schema
- Derived PHQ-2, HITS, GAD-2, physical-activity, and legal-access indicators
- Participant-facing success and validation-error messages
- Frontend behavioural regression tests with Vitest and React Testing Library
- Keyboard focus management and automated accessibility checks with axe-core

Supported question types:

- Single-select
- Multi-select
- Text
- Boolean
- Integer
- Currency
- Checklist
- Matrix

## Architecture

```mermaid
flowchart LR
    A["EU/GR questionnaire JSON"] --> B["FastAPI API"]
    B --> C["React frontend"]
    C --> D["Answer payload"]
    D --> B
    B --> E["JSON Schema validation"]
```

The backend serves the questionnaire definition and validates submitted responses. The frontend controls rendering, navigation, conditional visibility, and temporary in-memory answer state.

In production, the Docker build compiles the React application and FastAPI
serves the generated static files alongside the `/api/v1` routes from the same
origin. Local development continues to use Vite's proxy and FastAPI on port
`8001`.

## EU/Greek SD-DOH adaptation

The active questionnaire is:

```text
sdoh_screener_eu_gr_v2.json
```

Its corresponding response schema is:

```text
sdoh_screener_response_schema_eu_gr_v2.json
```

Important adaptations include:

- Required age group for age-specific activity interpretation
- Optional gender, ethnic-group, ancestry, and postal-code responses
- European-region questions
- Euro-based household income brackets
- Education and employment options adapted for European contexts
- Public and private healthcare-coverage categories
- EU-relevant transportation options
- PHQ-2 and GAD-2 screening matrices
- HITS intimate-partner-violence screening offered independently of the current-partner answer
- Self-reported cognition context without an MMSE field
- An I-HELP-informed legal-needs module
- A six-item Digital Access and Inclusion module

Religion/spiritual-belief items from the earlier adaptation were removed because they were not part of the intended source questionnaire and lacked a documented inclusion rationale. eHEALS is deliberately deferred to a separate HEALIE digital-literacy component.

The complete item-level decisions, rationale, sources, and paper-ready methods language are in [`SD_DOH_QUESTION_AUDIT.md`](SD_DOH_QUESTION_AUDIT.md).

The ontology mapping is stored in:

```text
sdoh_ontology_mapping_eu_gr_v2.json
```

## Requirements

The redesign has been developed and tested with:

- Python 3.13
- Node.js 24
- npm
- FastAPI
- React 19
- TypeScript
- Vite

Other recent Python and Node.js versions may also work, but these are the versions currently used during development.

## Local setup

Clone the repository and enter its directory:

```bash
git clone https://github.com/ckakalou/SDoH_Screener.git
cd SDoH_Screener
git switch redesign/react-fastapi
```

### Windows PowerShell

Create and activate a Python virtual environment:

```powershell
python -m venv SDoHScreener.venv
.\SDoHScreener.venv\Scripts\Activate.ps1
```

Install the backend development dependencies:

```powershell
python -m pip install -r backend/requirements-dev.txt
```

Install the frontend dependencies:

```powershell
npm.cmd --prefix frontend ci
```

### macOS or Linux

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the backend development dependencies:

```bash
python -m pip install -r backend/requirements-dev.txt
```

Install the frontend dependencies:

```bash
npm --prefix frontend ci
```

## Run the application

The backend and frontend run in separate terminals.

### 1. Start FastAPI

From the repository root:

```bash
python -m uvicorn backend.app.main:app --reload --port 8001
```

Available backend URLs:

- Health check: <http://127.0.0.1:8001/health>
- Questionnaire API: <http://127.0.0.1:8001/api/v1/screener>
- Swagger documentation: <http://127.0.0.1:8001/docs>
- ReDoc documentation: <http://127.0.0.1:8001/redoc>

### 2. Start React

On Windows:

```powershell
npm.cmd --prefix frontend run dev
```

On macOS or Linux:

```bash
npm --prefix frontend run dev
```

Open:

<http://localhost:5173>

During development, Vite proxies requests beginning with `/api` to the FastAPI backend on port `8001`.

## Production and Hugging Face Spaces

The repository is configured as a Hugging Face Docker Space. The multi-stage
`Dockerfile`:

1. installs the locked frontend dependencies with `npm ci`;
2. creates the Vite production build;
3. installs only the backend runtime dependencies;
4. copies the compiled frontend and active JSON contracts into a non-root
   Python runtime image; and
5. starts FastAPI on port `7860`.

FastAPI serves the compiled React interface at `/`, keeps `/api/v1/*` for the
application API, and continues to expose `/health`, `/docs`, and `/redoc`.
Unknown API paths return JSON `404` responses rather than the React page.

If Docker is available locally, test the production container from the
repository root:

```bash
docker build -t healie-sdoh-screener .
docker run --rm -p 7860:7860 healie-sdoh-screener
```

Then open <http://127.0.0.1:7860> and verify:

- <http://127.0.0.1:7860/health>
- <http://127.0.0.1:7860/api/v1/screener>
- <http://127.0.0.1:7860/docs>

The production container remains stateless: answers are held in browser memory
and only the derived indicator response is returned after final validation. No
database or persistent participant storage is introduced by this deployment.

To deploy, push the committed files to the Hugging Face Space repository. The
Space reads the YAML configuration at the top of this README, builds the
`Dockerfile`, and exposes port `7860`. Every pushed Space commit triggers a new
build and restart.

## API endpoints

### `GET /health`

Checks whether the backend is running.

Example response:

```json
{
  "status": "ok"
}
```

### `GET /api/v1/screener`

Returns the EU/GR SD-DOH questionnaire definition used by the React frontend.

### `POST /api/v1/screener/validate`

Validates submitted answers against the EU/GR response schema, visible-question requirements, and exclusive-answer rules.

Example request:

```json
{
  "responses": {
    "dem_age_group": "22_30",
    "q3_household_income": "20000_29999",
    "q11_internet": true,
    "q20a_pa_days": "3",
    "q20b_pa_minutes": 60,
    "ddoh_device_access": "always"
  }
}
```

Successful response:

```json
{
  "valid": true,
  "message": "The screener responses are valid.",
  "derived": {
    "assessment_id": "550e8400-e29b-41d4-a716-446655440000",
    "schema_version": "healie-sdoh-ddoh-indicators-1.0",
    "generated_at": "2026-10-14T07:30:00Z",
    "context": {
      "age": {
        "assessment_status": "assessed",
        "age_band": "22_30",
        "life_stage": "young_adult"
      }
    },
    "needs": {
      "physical_activity": {
        "assessment_status": "assessed",
        "weekly_minutes": 180,
        "need_identified": false
      }
    },
    "screening_results": {},
    "restricted_safety_indicators": {}
  }
}
```

The real response includes every field defined in
`healie_indicator_export_schema_v1.json`; the example above is abbreviated for
readability. The four tiers separate descriptive context, derived needs,
ordinary screening results, and restricted safety indicators.

`assessment_id` is a backend-generated UUIDv4 for one completed assessment
export. It is not a participant identifier, is not derived from answers, and is
new for every successful final full-assessment submission. Section checks do
not issue identifiers or indicator exports. `generated_at` records in UTC when
the backend created the export. A future HEALIE-wide pseudonymous `subject_id`,
if required for longitudinal use, must be managed separately and must not be
inferred from `assessment_id`.

A complete representative payload and field-level integration guidance are in
`healie_indicator_export_example_v1.json` and
`HEALIE_INTEGRATION_CONTRACT.md`.

Invalid values produce an HTTP `422` response containing the first validation error.

## Testing and quality checks

Run the backend tests:

```bash
python -m pytest backend/tests -v
```

On Windows, run the frontend checks with:

```powershell
npm.cmd --prefix frontend run lint
npm.cmd --prefix frontend run build
npm.cmd --prefix frontend test
```

On macOS or Linux:

```bash
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend test
```

Check staged or unstaged changes for whitespace errors:

```bash
git diff --check
```

A message stating that LF will be replaced by CRLF is an expected Git line-ending warning on Windows.

## Project structure

```text
SDoH_Screener/
├── Dockerfile
├── .dockerignore
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── models.py
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── public/
│   │   └── healie_final_official_logo_trans_crop.png
│   ├── src/
│   │   ├── api/
│   │   │   └── screenerApi.ts
│   │   ├── components/
│   │   │   ├── QuestionCard.tsx
│   │   │   └── UiIcon.tsx
│   │   ├── types/
│   │   │   └── screener.ts
│   │   ├── utils/
│   │   │   └── visibility.ts
│   │   ├── test/
│   │   │   └── setupTests.ts
│   │   ├── App.test.tsx
│   │   ├── App.tsx
│   │   └── App.css
│   ├── package.json
│   ├── vite.config.ts
│   └── vitest.config.ts
├── sdoh_screener_eu_gr_v2.json
├── sdoh_screener_response_schema_eu_gr_v2.json
├── sdoh_ontology_mapping_eu_gr_v2.json
├── healie_indicator_export_schema_v1.json
├── healie_indicator_export_example_v1.json
├── HEALIE_INTEGRATION_CONTRACT.md
├── SD_DOH_QUESTION_AUDIT.md
├── emit_rdf_eu_gr_v2.py
├── app.py
└── app_eu_gr_v2.py
```

## Legacy Streamlit prototypes

The repository retains the original Streamlit applications for reference:

- `app.py`: original questionnaire prototype
- `app_eu_gr_v2.py`: EU/GR-adapted Streamlit prototype
- `README_eu_gr_v2.md`: documentation for the EU/GR Streamlit version

The React/FastAPI implementation is the active redesign.

## Current limitations

The current redesign:

- Stores answers only in React memory
- Resets answers after a full browser refresh
- Does not persist responses in a database
- Does not include authentication or participant consent
- Requires every visible question except those explicitly marked optional
- Returns the versioned four-tier indicator contract but does not provide diagnosis or clinical decision support
- Still includes a development-only answer-state inspector
- Requires cognitive interviewing, translation/back-translation, accessibility review, and psychometric validation
- Uses project-authored legal and digital modules that must not be described as validated scales

## Safety and privacy

Production deployment will require:

- An appropriate consent process
- GDPR-compliant data handling
- Secure storage and transport
- Access control and authentication
- A defined retention and deletion policy
- A locally approved safety protocol for sensitive screening areas, including intimate-partner violence
- Clear clinical-governance boundaries explaining that screening results are not a diagnosis
