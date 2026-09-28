import type {
  AnswerValue,
  ScreenerQuestion,
} from '../types/screener'

interface QuestionCardProps {
  question: ScreenerQuestion
  value: AnswerValue | undefined
  onChange: (questionId: string, value: AnswerValue) => void
}

export function QuestionCard({
  question,
  value,
  onChange,
}: QuestionCardProps) {
  const selectedValues = Array.isArray(value)
    ? value.map(String)
    : []

  function handleMultiSelectChange(
    optionValue: string,
    checked: boolean,
  ) {
    const updatedValues = checked
      ? [...selectedValues, optionValue]
      : selectedValues.filter(
          (selectedValue) => selectedValue !== optionValue,
        )

    onChange(question.id, updatedValues)
  }

  function renderInput() {
    switch (question.type) {
      case 'multi-select':
        return question.options?.map((option) => {
          const optionValue = String(option.value)

          return (
            <label key={optionValue}>
              <input
                type="checkbox"
                name={question.id}
                value={optionValue}
                checked={selectedValues.includes(optionValue)}
                onChange={(event) =>
                  handleMultiSelectChange(
                    optionValue,
                    event.target.checked,
                  )
                }
              />

              {option.label}

              {option.free_text_hint && (
                <small>{option.free_text_hint}</small>
              )}
            </label>
          )
        })

      case 'single-select':
        return question.options?.map((option) => (
          <label key={String(option.value)}>
            <input
              type="radio"
              name={question.id}
              value={String(option.value)}
              checked={value === option.value}
              onChange={() =>
                onChange(question.id, option.value)
              }
            />

            {option.label}
          </label>
        ))

      case 'text':
        return (
          <input
            id={question.id}
            type="text"
            value={typeof value === 'string' ? value : ''}
            placeholder={question.placeholder}
            onChange={(event) =>
              onChange(question.id, event.target.value)
            }
          />
        )

      default:
        return (
          <p>
            Question type <code>{question.type}</code> is not implemented yet.
          </p>
        )
    }
  }

  return (
    <article className="question-card">
      <p>Section {question.section}</p>

      <fieldset>
        <legend>{question.text}</legend>
        {renderInput()}
      </fieldset>
    </article>
  )
}