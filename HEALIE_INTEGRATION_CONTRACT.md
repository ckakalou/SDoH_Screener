# HEALIE SD-DOH integration contract

## Purpose

The SD-DOH component validates questionnaire responses and returns a
data-minimised indicator export for the wider HEALIE system. The integration
boundary is the `derived` object returned by:

```text
POST /api/v1/screener/validate
```

The wider system should consume the derived contract, not retain or forward the
submitted `responses` object unless a separately governed research protocol is
introduced.

## Request

```json
{
  "responses": {
    "dem_age_group": "22_30"
  }
}
```

The optional `section` field supports section-level validation in the
participant interface. A successful section check returns an empty `derived`
object and does not issue an assessment UUID. Omit `section` for final
full-assessment validation and indicator export.

## Successful response

```json
{
  "valid": true,
  "message": "The screener responses are valid.",
  "derived": {
    "assessment_id": "550e8400-e29b-41d4-a716-446655440000",
    "schema_version": "healie-sdoh-ddoh-indicators-1.0",
    "generated_at": "2026-10-14T07:30:00Z",
    "context": {},
    "needs": {},
    "screening_results": {},
    "restricted_safety_indicators": {}
  }
}
```

The objects above are abbreviated. The authoritative structure is
`healie_indicator_export_schema_v1.json`; a complete representative instance is
`healie_indicator_export_example_v1.json`.

## Envelope fields

| Field | Meaning | Integration rule |
| --- | --- | --- |
| `assessment_id` | Random UUIDv4 identifying one export event | Use for tracing and deduplication; never treat as a participant ID |
| `schema_version` | Version of the indicator contract | Consumers must reject or explicitly migrate unsupported versions |
| `generated_at` | UTC creation time in RFC 3339/ISO 8601 form | Use as export provenance, not as questionnaire completion duration |
| `context` | Approved descriptive information | Restrict use to relevance, accessibility and governed linkage |
| `needs` | Derived nullable needs and barriers | `null` means unknown/not assessed, not absence of need |
| `screening_results` | Non-safety screening outputs | Screening is non-diagnostic |
| `restricted_safety_indicators` | Safety-sensitive outputs | Apply separate authorization and logging controls |

## Identity boundary

`assessment_id` identifies an assessment, not a person. Repeating the screener
creates a different UUID. It must not be derived from demographics, postal
code, answers, browser/device information or credentials.

If HEALIE later supports longitudinal linkage, its identity service may attach
a separate pseudonymous `subject_id` outside this component. That future field
must have an explicit purpose, retention period and access-control policy.

## Data-minimisation boundary

The operational export intentionally excludes raw PHQ-2, GAD-2 and HITS items,
most free text, thresholds, MMSE data, personalisation weights and the complete
verbatim response record. Ancestry and the explicitly approved contextual
fields are documented exceptions.

Postal code requires controlled geographic enrichment and should not be sent
to a general-purpose language-model prompt. Restricted safety indicators must
not be exposed to ordinary content-personalisation services.

## Error behavior

Invalid values, missing visible required answers and exclusive-answer conflicts
return HTTP `422`. Consumers must not treat a failed validation as a completed
assessment and must not manufacture a derived payload client-side.

## Consumer checklist

- Validate the payload against `healie_indicator_export_schema_v1.json`.
- Record and support the exact `schema_version`.
- Use `assessment_id` only for assessment-level tracing and deduplication.
- Preserve `null` and explicit assessment-status values.
- Apply stricter access controls to `restricted_safety_indicators`.
- Do not persist or forward verbatim answers as part of normal HEALIE operation.
