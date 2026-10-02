import type {
  ScreenerAnswers,
  ScreenerApiResponse,
  ScreenerValidationResult,
} from '../types/screener'

const SCREENER_ENDPOINT = '/api/v1/screener'
const VALIDATION_ENDPOINT = '/api/v1/screener/validate'

export async function fetchScreener(): Promise<ScreenerApiResponse> {
  const response = await fetch(SCREENER_ENDPOINT)

  if (!response.ok) {
    throw new Error(
      `Could not load the screener: ${response.status} ${response.statusText}`,
    )
  }

  return response.json() as Promise<ScreenerApiResponse>
}

export async function validateScreener(
  answers: ScreenerAnswers,
  section?: number,
): Promise<ScreenerValidationResult> {
  const response = await fetch(VALIDATION_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      responses: answers,
      ...(section === undefined ? {} : { section }),
    }),
  })

  if (!response.ok) {
    const errorBody = (await response.json()) as {
      detail?: string
    }

    throw new Error(
      errorBody.detail ??
        `Could not validate the screener: ${response.status} ${response.statusText}`,
    )
  }

  return response.json() as Promise<ScreenerValidationResult>
}
