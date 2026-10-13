import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import axe from 'axe-core'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import {
  fetchScreener,
  validateScreener,
} from './api/screenerApi'
import type {
  ScreenerApiResponse,
  ScreenerValidationResult,
} from './types/screener'

vi.mock('./api/screenerApi', () => ({
  fetchScreener: vi.fn(),
  validateScreener: vi.fn(),
}))

const mockFetchScreener = vi.mocked(fetchScreener)
const mockValidateScreener = vi.mocked(validateScreener)

const screenerResponse: ScreenerApiResponse = {
  screener: {
    title: 'Test assessment',
    version: 'test',
    created: '2026-10-09',
    language: 'en',
    notes: [],
    context_fields: [],
    computed: [],
    flags: [],
    ui: {
      pagination: 'sectioned',
      show_progress: true,
      allow_skip: false,
    },
    questions: [
      {
        id: 'needs_support',
        section: 1,
        text: 'Do you need support?',
        type: 'single-select',
        required: true,
        options: [
          { value: 'yes', label: 'Yes' },
          { value: 'no', label: 'No' },
        ],
      },
      {
        id: 'support_details',
        section: 1,
        text: 'What support do you need?',
        type: 'text',
        required: false,
        visible_if: {
          all: [
            {
              question: 'needs_support',
              operator: '=',
              value: 'yes',
            },
          ],
        },
      },
      {
        id: 'preferred_colour',
        section: 2,
        text: 'Choose a colour',
        type: 'single-select',
        required: true,
        options: [
          { value: 'blue', label: 'Blue' },
          { value: 'green', label: 'Green' },
        ],
      },
    ],
  },
}

const validResult: ScreenerValidationResult = {
  valid: true,
  message: 'Responses are valid.',
  derived: {
    schema_version: 'healie-sdoh-ddoh-indicators-1.0',
    context: {
      age: {
        assessment_status: 'assessed',
        age_band: '22_30',
      },
    },
    needs: {},
    screening_results: {},
    restricted_safety_indicators: {},
  },
}

async function renderLoadedApp() {
  render(<App />)

  await screen.findByRole('heading', {
    name: 'Do you need support?',
  })
  return userEvent.setup()
}

describe('App questionnaire behaviour', () => {
  beforeEach(() => {
    mockFetchScreener.mockResolvedValue(screenerResponse)
    mockValidateScreener.mockResolvedValue(validResult)
  })

  it('blocks navigation when a visible required question is unanswered', async () => {
    const user = await renderLoadedApp()

    await user.click(screen.getByRole('button', { name: /continue/i }))

    const alert = screen.getByRole('alert')
    expect(alert).toHaveTextContent(
      'Please answer “Do you need support?” before continuing.',
    )
    expect(alert).toHaveFocus()
    expect(mockValidateScreener).not.toHaveBeenCalled()
    expect(screen.getAllByText('Section 1 of 2')).not.toHaveLength(0)
  })

  it('shows conditional questions and clears their stale answers when hidden', async () => {
    const user = await renderLoadedApp()

    await user.click(screen.getByRole('radio', { name: 'Yes' }))

    const details = screen.getByRole('textbox', {
      name: 'What support do you need?',
    })
    await user.type(details, 'Transport assistance')
    expect(details).toHaveValue('Transport assistance')

    await user.click(screen.getByRole('radio', { name: 'No' }))
    expect(
      screen.queryByRole('textbox', {
        name: 'What support do you need?',
      }),
    ).not.toBeInTheDocument()

    await user.click(screen.getByRole('radio', { name: 'Yes' }))
    expect(
      screen.getByRole('textbox', {
        name: 'What support do you need?',
      }),
    ).toHaveValue('')
  })

  it('keeps answers selected while moving between sections', async () => {
    const user = await renderLoadedApp()

    await user.click(screen.getByRole('radio', { name: 'No' }))
    await user.click(screen.getByRole('button', { name: /continue/i }))

    const nextSectionHeading = await screen.findByRole('heading', {
      name: 'Choose a colour',
    })
    expect(nextSectionHeading).toHaveFocus()
    expect(mockValidateScreener).toHaveBeenCalledWith(
      { needs_support: 'no' },
      1,
    )

    await user.click(screen.getByRole('button', { name: /previous/i }))

    expect(screen.getByRole('radio', { name: 'No' })).toBeChecked()
  })

  it('shows the completion screen after a successful submission', async () => {
    const user = await renderLoadedApp()

    await user.click(screen.getByRole('radio', { name: 'No' }))
    await user.click(screen.getByRole('button', { name: /continue/i }))
    await screen.findByRole('heading', { name: 'Choose a colour' })
    await user.click(screen.getByRole('radio', { name: 'Blue' }))
    await user.click(
      screen.getByRole('button', { name: /submit answers/i }),
    )

    const completionHeading = await screen.findByRole('heading', {
      name: 'Thank you',
    })
    expect(completionHeading).toHaveFocus()
    expect(screen.getByRole('img', { name: 'Healie' })).toHaveAttribute(
      'src',
      '/healie_final_official_logo_full.png',
    )
    expect(
      screen.getByText('Social and digital factors affecting health'),
    ).toBeInTheDocument()
    expect(mockValidateScreener).toHaveBeenLastCalledWith({
      needs_support: 'no',
      preferred_colour: 'blue',
    })

    const preview = screen.getByText(
      'Development: indicator export preview',
    )
    expect(preview).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Download indicator JSON' }),
    ).toHaveAttribute(
      'download',
      'healie-sdoh-ddoh-indicators.json',
    )
    expect(screen.getByText(/healie-sdoh-ddoh-indicators-1\.0/)).toBeInTheDocument()
  })

  it('shows a server validation message without completing', async () => {
    const user = await renderLoadedApp()

    await user.click(screen.getByRole('radio', { name: 'No' }))
    await user.click(screen.getByRole('button', { name: /continue/i }))
    await screen.findByRole('heading', { name: 'Choose a colour' })
    await user.click(screen.getByRole('radio', { name: 'Green' }))

    mockValidateScreener.mockResolvedValueOnce({
      valid: false,
      message: 'Please review your answers.',
      derived: {},
    })

    await user.click(
      screen.getByRole('button', { name: /submit answers/i }),
    )

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Please review your answers.',
      )
    })
    expect(
      screen.queryByRole('heading', { name: 'Thank you' }),
    ).not.toBeInTheDocument()
  })

  it('has no automatically detectable accessibility violations', async () => {
    const { container } = render(<App />)

    await screen.findByRole('heading', {
      name: 'Do you need support?',
    })

    const results = await axe.run(container, {
      rules: {
        'color-contrast': { enabled: false },
      },
    })
    expect(results.violations).toEqual([])
  })
})
