import type {
  AnswerValue,
  ScreenerAnswers,
  VisibilityCondition,
  VisibilityRule,
} from '../types/screener'

function getAnswer(
  questionId: string,
  answers: ScreenerAnswers,
): AnswerValue | undefined {
  const directAnswer = answers[questionId]

  if (directAnswer !== undefined) {
    return directAnswer
  }

  for (const answer of Object.values(answers)) {
    if (
      typeof answer === 'object' &&
      answer !== null &&
      !Array.isArray(answer) &&
      questionId in answer
    ) {
      return answer[questionId]
    }
  }

  return undefined
}

function conditionMatches(
  condition: VisibilityCondition,
  answers: ScreenerAnswers,
) {
  const answer = getAnswer(condition.question, answers)

  switch (condition.operator) {
    case '=':
      return answer === condition.value
    case 'contains':
      return (
        Array.isArray(answer) &&
        answer.includes(String(condition.value))
      )
    default:
      return false
  }
}

export function isQuestionVisible(
  rule: VisibilityRule | undefined,
  answers: ScreenerAnswers,
) {
  if (!rule) {
    return true
  }

  const anyMatches = rule.any
    ? rule.any.some((condition) =>
        conditionMatches(condition, answers),
      )
    : true

  const allMatch = rule.all
    ? rule.all.every((condition) =>
        conditionMatches(condition, answers),
      )
    : true

  return anyMatches && allMatch
}
