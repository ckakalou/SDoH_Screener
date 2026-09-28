import { useEffect, useState } from 'react'
import { fetchScreener } from './api/screenerApi'
import { QuestionCard } from './components/QuestionCard'
import type {
  AnswerValue,
  ScreenerAnswers,
  ScreenerDefinition,
} from './types/screener'
import './App.css'


function App() {
  const [screener, setScreener] = useState<ScreenerDefinition | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [answers, setAnswers] = useState<ScreenerAnswers>({})

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

const firstQuestions = screener.questions.slice(0, 3)

function handleAnswerChange(questionId: string, value: AnswerValue) {
  setAnswers((currentAnswers) => ({
    ...currentAnswers,
    [questionId]: value,
  }))
}

return (
  <main>
    <header>
      <h1>{screener.title}</h1>
      <p>Version: {screener.version}</p>
      <p>Questions received: {screener.questions.length}</p>
    </header>

<section aria-label="Screener questions">
  {firstQuestions.length > 0 ? (
    firstQuestions.map((question) => (
      <QuestionCard
        key={question.id}
        question={question}
        value={answers[question.id]}
        onChange={handleAnswerChange}
      />
    ))
  ) : (
    <p>No questions were returned by the API.</p>
  )}
</section>

    <section>
      <h2>Current answer state</h2>
      <pre>{JSON.stringify(answers, null, 2)}</pre>
    </section>
  </main>
)
}

export default App
