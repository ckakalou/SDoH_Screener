import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { QuestionCard } from './QuestionCard'
import type { ScreenerQuestion } from '../types/screener'

const checklistQuestion: ScreenerQuestion = {
  id: 'unmet_needs',
  section: 16,
  text: 'Have you had any unmet needs?',
  type: 'checklist',
  required: true,
  exclusive_item_id: 'decline',
  items: [
    { id: 'food', label: 'Food', type: 'boolean' },
    {
      id: 'decline',
      label: 'Prefer not to answer',
      type: 'boolean',
    },
  ],
}

describe('QuestionCard exclusive checklist behaviour', () => {
  it('clears substantive checklist answers when decline is selected', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(
      <QuestionCard
        question={checklistQuestion}
        value={{ food: true, decline: false }}
        onChange={onChange}
      />,
    )

    await user.click(
      screen.getByRole('checkbox', {
        name: /choose not to answer/i,
      }),
    )

    expect(onChange).toHaveBeenCalledWith('unmet_needs', {
      decline: true,
    })
  })

  it('clears decline when a substantive checklist answer is selected', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(
      <QuestionCard
        question={checklistQuestion}
        value={{ decline: true }}
        onChange={onChange}
      />,
    )

    const foodRow = screen.getByRole('group', { name: 'Food' })
    await user.click(within(foodRow).getByRole('radio', { name: 'Yes' }))

    expect(onChange).toHaveBeenCalledWith('unmet_needs', {
      decline: false,
      food: true,
    })
  })
})

describe('QuestionCard compact scale behaviour', () => {
  it('renders a numeric scale as compact radio choices', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    const question: ScreenerQuestion = {
      id: 'activity_days',
      section: 20,
      text: 'How many days?',
      help_text: 'Choose one value.',
      type: 'single-select',
      display_variant: 'compact-scale',
      options: [
        { value: '0', label: '0' },
        { value: '1', label: '1' },
        { value: '2', label: '2' },
      ],
    }

    const { container } = render(
      <QuestionCard
        question={question}
        value="1"
        onChange={onChange}
      />,
    )

    expect(screen.getByText('Choose one value.')).toBeInTheDocument()
    expect(container.querySelector('.compact-scale-options')).not.toBeNull()
    expect(screen.getByRole('radio', { name: '1' })).toBeChecked()

    await user.click(screen.getByRole('radio', { name: '2' }))
    expect(onChange).toHaveBeenCalledWith('activity_days', '2')
  })
})
