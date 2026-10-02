import type {
  AnswerValue,
  ScreenerQuestion,
  StructuredAnswer,
} from '../types/screener'
import { UiIcon } from './UiIcon'

function isStructuredAnswer(
  value: AnswerValue | undefined,
): value is StructuredAnswer {
  return (
    typeof value === 'object' &&
    value !== null &&
    !Array.isArray(value)
  )
}

interface QuestionCardProps {
  question: ScreenerQuestion
  value: AnswerValue | undefined
  onChange: (questionId: string, value: AnswerValue) => void
  hideQuestionText?: boolean
}

export function QuestionCard({
  question,
  value,
  onChange,
  hideQuestionText = false,
}: QuestionCardProps) {
  const selectedValues = Array.isArray(value)
    ? value.map(String)
    : []
  const structuredValue = isStructuredAnswer(value) ? value : {}

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
        return (
          <div className="answer-options">
            {question.options?.map((option) => {
              const optionValue = String(option.value)

              return (
                <label className="answer-option" key={optionValue}>
                  <input
                    className="answer-input"
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
                  <span className="option-copy">
                    {option.label}
                    {option.free_text_hint && (
                      <small>{option.free_text_hint}</small>
                    )}
                  </span>
                  <span className="selection-mark" aria-hidden="true">
                    <UiIcon name="check" />
                  </span>
                </label>
              )
            })}
          </div>
        )

      case 'single-select':
        return (
          <div className="answer-options">
            {question.options?.map((option) => (
              <label
                className="answer-option"
                key={String(option.value)}
              >
                <input
                  className="answer-input"
                  type="radio"
                  name={question.id}
                  value={String(option.value)}
                  checked={value === option.value}
                  onChange={() =>
                    onChange(question.id, option.value)
                  }
                />
                <span className="option-copy">{option.label}</span>
                <span className="selection-mark" aria-hidden="true">
                  <UiIcon name="check" />
                </span>
              </label>
            ))}
          </div>
        )

      case 'text':
        return (
          <input
            className="text-field"
            id={question.id}
            type="text"
            value={typeof value === 'string' ? value : ''}
            placeholder={question.placeholder}
            onChange={(event) =>
              onChange(question.id, event.target.value)
            }
          />
        )

      case 'boolean':
        return (
          <div className="binary-options">
            <label className="binary-option">
              <input
                className="answer-input"
                type="radio"
                name={question.id}
                checked={value === true}
                onChange={() => onChange(question.id, true)}
              />
              <span>Yes</span>
            </label>
            <label className="binary-option">
              <input
                className="answer-input"
                type="radio"
                name={question.id}
                checked={value === false}
                onChange={() => onChange(question.id, false)}
              />
              <span>No</span>
            </label>
          </div>
        )

      case 'integer':
        return (
          <input
            className="text-field number-field"
            id={question.id}
            type="number"
            min={question.min}
            max={question.max}
            step={1}
            inputMode="numeric"
            aria-label={question.text}
            value={typeof value === 'number' ? value : ''}
            onChange={(event) => {
              const rawValue = event.target.value

              onChange(
                question.id,
                rawValue === ''
                  ? ''
                  : Number.parseInt(rawValue, 10),
              )
            }}
          />
        )

      case 'currency':
        return (
          <label className="currency-field">
            <span aria-hidden="true">€</span>
            <input
              className="text-field"
              id={question.id}
              type="number"
              min={question.min ?? 0}
              max={question.max}
              step="0.01"
              inputMode="decimal"
              aria-label={`${question.text} in euros`}
              value={typeof value === 'number' ? value : ''}
              onChange={(event) => {
                const rawValue = event.target.value

                onChange(
                  question.id,
                  rawValue === '' ? '' : Number(rawValue),
                )
              }}
            />
          </label>
        )

      case 'checklist':
        return (
          <div className="structured-list">
            {question.items?.map((item) => (
              <fieldset className="structured-row" key={item.id}>
                <legend>{item.label}</legend>
                <div className="row-choices">
                  <label className="compact-choice">
                    <input
                      className="answer-input"
                      type="radio"
                      name={item.id}
                      checked={structuredValue[item.id] === true}
                      onChange={() =>
                        onChange(question.id, {
                          ...structuredValue,
                          [item.id]: true,
                        })
                      }
                    />
                    <span>Yes</span>
                  </label>
                  <label className="compact-choice">
                    <input
                      className="answer-input"
                      type="radio"
                      name={item.id}
                      checked={structuredValue[item.id] === false}
                      onChange={() =>
                        onChange(question.id, {
                          ...structuredValue,
                          [item.id]: false,
                        })
                      }
                    />
                    <span>No</span>
                  </label>
                </div>
              </fieldset>
            ))}
          </div>
        )

      case 'matrix':
        return (
          <div
            className="structured-list matrix-list"
            role="group"
            aria-label={question.text}
          >
            {question.rows?.map((row) => (
              <fieldset className="matrix-row" key={row.id}>
                <legend>{row.label}</legend>
                <div className="matrix-choices">
                  {question.scale?.map((scaleOption) => (
                    <label
                      className="matrix-choice"
                      key={scaleOption.value}
                    >
                      <input
                        className="answer-input"
                        type="radio"
                        name={row.id}
                        value={scaleOption.value}
                        checked={
                          structuredValue[row.id] === scaleOption.value
                        }
                        onChange={() =>
                          onChange(question.id, {
                            ...structuredValue,
                            [row.id]: scaleOption.value,
                          })
                        }
                      />
                      <span>{scaleOption.label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>
            ))}
          </div>
        )

      default:
        return (
          <p className="unsupported-question">
            Question type <code>{question.type}</code> is not
            implemented yet.
          </p>
        )
    }
  }

  return (
    <article className="question-card">
      <fieldset className="question-fieldset">
        <legend className={hideQuestionText ? 'visually-hidden' : ''}>
          {question.text}
        </legend>
        {renderInput()}
      </fieldset>
    </article>
  )
}
