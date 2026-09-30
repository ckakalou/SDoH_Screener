# SDoH Screener

A schema-driven Social Determinants of Health (SDoH) screening application developed as part of the HEALIE research project.

The current redesign uses:

- React and TypeScript for the frontend
- FastAPI for the backend API
- JSON Schema for response validation
- An EU/Greek-adapted questionnaire definition

> Research software under active development. It is not currently intended for clinical use.

## Current functionality

The React/FastAPI implementation currently supports:

- Loading the questionnaire definition from FastAPI
- Rendering questions dynamically from the EU/GR v2 JSON configuration
- Section-by-section navigation with progress feedback
- Shared answer state across all sections
- Conditional visibility using `any` and `all` rules
- Automatic removal of answers when conditional questions become hidden
- Submission of answers to FastAPI
- Server-side validation using JSON Schema
- Participant-facing success and validation-error messages

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

## EU/Greek adaptation

The active questionnaire is:

```text
sdoh_screener_eu_gr_v2.json
```

Its corresponding response schema is:

```text
sdoh_screener_response_schema_eu_gr_v2.json
```

Important adaptations include:

- Ethnic-group and European-region questions
- Euro-based household income brackets
- Education and employment options adapted for European contexts
- Public and private healthcare-coverage categories
- EU-relevant transportation options
- PHQ-2 and GAD-2 screening matrices
- Optional self-reported cognition and MMSE total fields
- Digital-device access
- Religion or spiritual-belief options with conditional free text

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

Returns the EU/GR v2 questionnaire definition used by the React frontend.

### `POST /api/v1/screener/validate`

Validates submitted answers against the EU/GR v2 response schema.

Example request:

```json
{
  "responses": {
    "q3_household_income": "20000_29999",
    "q11_internet": true,
    "q20b_pa_minutes": 30,
    "q23_digital_device_access": "yes"
  }
}
```

Successful response:

```json
{
  "valid": true,
  "message": "The screener responses are valid."
}
```

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
```

On macOS or Linux:

```bash
npm --prefix frontend run lint
npm --prefix frontend run build
```

Check staged or unstaged changes for whitespace errors:

```bash
git diff --check
```

A message stating that LF will be replaced by CRLF is an expected Git line-ending warning on Windows.

## Project structure

```text
SDoH_Screener/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── models.py
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── screenerApi.ts
│   │   ├── components/
│   │   │   └── QuestionCard.tsx
│   │   ├── types/
│   │   │   └── screener.ts
│   │   ├── utils/
│   │   │   └── visibility.ts
│   │   ├── App.tsx
│   │   └── App.css
│   ├── package.json
│   └── vite.config.ts
├── sdoh_screener_eu_gr_v2.json
├── sdoh_screener_response_schema_eu_gr_v2.json
├── sdoh_ontology_mapping_eu_gr_v2.json
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
- Validates supplied answers but does not require questionnaire completion
- Does not yet calculate the derived scores and SDoH flags available in the Streamlit prototype
- Still includes a development-only answer-state inspector
- Requires a separate content-validation review for the Section 16 follow-up logic

## Safety and privacy

Production deployment will require:

- An appropriate consent process
- GDPR-compliant data handling
- Secure storage and transport
- Access control and authentication
- A defined retention and deletion policy
- A locally approved safety protocol for sensitive screening areas, including intimate-partner violence
- Clear clinical-governance boundaries explaining that screening results are not a diagnosis

