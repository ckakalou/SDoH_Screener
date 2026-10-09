import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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
  derived: {},
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

    expect(
      screen.getByRole('alert'),
    ).toHaveTextContent(
      'Please answer “Do you need support?” before continuing.',
    )
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

    await screen.findByRole('heading', { name: 'Choose a colour' })
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

    expect(
      await screen.findByRole('heading', { name: 'Thank you' }),
    ).toBeInTheDocument()
    expect(mockValidateScreener).toHaveBeenLastCalledWith({
      needs_support: 'no',
      preferred_colour: 'blue',
    })
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
})
