import type { ScreenerApiResponse } from '../types/screener'

const SCREENER_ENDPOINT = '/api/v1/screener'

export async function fetchScreener(): Promise<ScreenerApiResponse> {
  const response = await fetch(SCREENER_ENDPOINT)

  if (!response.ok) {
    throw new Error(
      `Could not load the screener: ${response.status} ${response.statusText}`,
    )
  }

  return response.json() as Promise<ScreenerApiResponse>
}