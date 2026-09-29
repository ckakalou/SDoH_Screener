import type {
  AnswerValue,
  ScreenerQuestion,
  StructuredAnswer,
} from '../types/screener'

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
}

export function QuestionCard({
  question,
  value,
  onChange,
}: QuestionCardProps) {
  const selectedValues = Array.isArray(value)
    ? value.map(String)
    : []
const structuredValue = isStructuredAnswer(value)
  ? value
  : {}
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
        case "boolean":
  return (
    <fieldset aria-label={question.text}>
      <label>
        <input

          type="radio"
          name={question.id}
          checked={value === true}
          onChange={() => onChange(question.id, true)}
        />
        Yes
      </label>

      <label>
        <input
          type="radio"
          name={question.id}
          checked={value === false}
          onChange={() => onChange(question.id, false)}
        />
        No
      </label>
    </fieldset>
  )

case "integer":
  return (
    <input
      id={question.id}
      type="number"
      step={1}
      inputMode="numeric"
      aria-label={question.text}
      value={typeof value === "number" ? value : ""}
      onChange={(event) => {
        const rawValue = event.target.value

        onChange(
          question.id,
          rawValue === "" ? "" : Number.parseInt(rawValue, 10),
        )
      }}
    />
  )

case "currency":
  return (
    <label>
      <span>€</span>

      <input
        id={question.id}
        type="number"
        min={0}
        step="0.01"
        inputMode="decimal"
        aria-label={`${question.text} in euros`}
        value={typeof value === "number" ? value : ""}
        onChange={(event) => {
          const rawValue = event.target.value

          onChange(
            question.id,
            rawValue === "" ? "" : Number(rawValue),
          )
        }}
      />
    </label>
  )
case 'checklist':
  return question.items?.map((item) => (
    <fieldset key={item.id}>
      <legend>{item.label}</legend>

      <label>
        <input
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
        Yes
      </label>

      <label>
        <input
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
        No
      </label>
    </fieldset>
  ))
        case 'matrix':
  return (
    <div role="group" aria-label={question.text}>
      {question.rows?.map((row) => (
        <fieldset key={row.id}>
          <legend>{row.label}</legend>

          {question.scale?.map((scaleOption) => (
            <label key={scaleOption.value}>
              <input
                type="radio"
                name={row.id}
                value={scaleOption.value}
                checked={
                  structuredValue[row.id] ===
                  scaleOption.value
                }
                onChange={() =>
                  onChange(question.id, {
                    ...structuredValue,
                    [row.id]: scaleOption.value,
                  })
                }
              />

              {scaleOption.label}
            </label>
          ))}
        </fieldset>
      ))}
    </div>
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

      <fieldset>
        <legend>{question.text}</legend>
        {renderInput()}
      </fieldset>
    </article>
  )
}