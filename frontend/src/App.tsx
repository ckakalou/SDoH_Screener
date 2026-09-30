import { useEffect, useState } from 'react'
import {
  fetchScreener,
  validateScreener,
} from './api/screenerApi'
import { QuestionCard } from './components/QuestionCard'
import type {
  AnswerValue,
  ScreenerAnswers,
  ScreenerDefinition,
} from './types/screener'
import { isQuestionVisible } from './utils/visibility'
import './App.css'

function App() {
  const [screener, setScreener] =
    useState<ScreenerDefinition | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [answers, setAnswers] = useState<ScreenerAnswers>({})
  const [currentSectionIndex, setCurrentSectionIndex] =
    useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submissionMessage, setSubmissionMessage] =
    useState<string | null>(null)
  const [submissionSucceeded, setSubmissionSucceeded] =
    useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadScreener() {
      try {
        const response = await fetchScreener()

        if (!cancelled) {
          setScreener(response.screener)
        }
      } catch (caughtError) {
        if (!cancelled) {
          const message =
            caughtError instanceof Error
              ? caughtError.message
              : 'An unexpected error occurred.'

          setError(message)
        }
      }
    }

    loadScreener()

    return () => {
      cancelled = true
    }
  }, [])

  if (error) {
    return (
      <main>
        <h1>Unable to load the screener</h1>
        <p>{error}</p>
      </main>
    )
  }

  if (!screener) {
    return (
      <main>
        <p>Loading screener…</p>
      </main>
    )
  }

  const questions = screener.questions

  const sections = Array.from(
    new Set(
      questions.map((question) => question.section),
    ),
  )

  const currentSection = sections[currentSectionIndex]

  const visibleQuestions = questions.filter(
    (question) =>
      question.section === currentSection &&
      isQuestionVisible(question.visible_if, answers),
  )

  const isFirstSection = currentSectionIndex === 0
  const isLastSection =
    currentSectionIndex === sections.length - 1

  function handleAnswerChange(
    questionId: string,
    value: AnswerValue,
  ) {
    setSubmissionMessage(null)
    setSubmissionSucceeded(false)

    setAnswers((currentAnswers) => {
      const updatedAnswers: ScreenerAnswers = {
        ...currentAnswers,
        [questionId]: value,
      }

      for (const question of questions) {
        if (
          !isQuestionVisible(
            question.visible_if,
            updatedAnswers,
          )
        ) {
          delete updatedAnswers[question.id]
        }
      }

      return updatedAnswers
    })
  }

  async function handleSubmit() {
    setIsSubmitting(true)
    setSubmissionMessage(null)
    setSubmissionSucceeded(false)

    try {
      const result = await validateScreener(answers)

      setSubmissionMessage(result.message)
      setSubmissionSucceeded(result.valid)
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : 'An unexpected error occurred.'

      setSubmissionMessage(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  function changeSection(nextIndex: number) {
    setCurrentSectionIndex(nextIndex)

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  return (
    <main>
      <header>
        <h1>{screener.title}</h1>
        <p>Version: {screener.version}</p>

        <p aria-live="polite">
          Step {currentSectionIndex + 1} of{' '}
          {sections.length}
        </p>

        <progress
          aria-label="Screener progress"
          value={currentSectionIndex + 1}
          max={sections.length}
        />
      </header>

      <section aria-labelledby="section-heading">
        <h2 id="section-heading">
          Section {currentSection}
        </h2>

        {visibleQuestions.length > 0 ? (
          visibleQuestions.map((question) => (
            <QuestionCard
              key={question.id}
              question={question}
              value={answers[question.id]}
              onChange={handleAnswerChange}
            />
          ))
        ) : (
          <p>
            No questions are available in this section.
          </p>
        )}
      </section>

      <nav aria-label="Screener section navigation">
        <button
          type="button"
          disabled={isFirstSection}
          onClick={() =>
            changeSection(currentSectionIndex - 1)
          }
        >
          Previous
        </button>

        {isLastSection ? (
          <button
            type="button"
            disabled={isSubmitting}
            onClick={handleSubmit}
          >
            {isSubmitting
              ? 'Submitting…'
              : 'Submit answers'}
          </button>
        ) : (
          <button
            type="button"
            onClick={() =>
              changeSection(currentSectionIndex + 1)
            }
          >
            Next
          </button>
        )}
      </nav>

      {submissionMessage && (
        <p
          role={
            submissionSucceeded ? 'status' : 'alert'
          }
        >
          {submissionMessage}
        </p>
      )}

      <details>
        <summary>
          Development: current answer state
        </summary>
        <pre>{JSON.stringify(answers, null, 2)}</pre>
      </details>
    </main>
  )
}

export default App