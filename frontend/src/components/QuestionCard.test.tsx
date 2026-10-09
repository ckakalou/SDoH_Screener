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
