import { useEffect, useState } from 'react'
import {
  fetchScreener,
  validateScreener,
} from './api/screenerApi'
import { QuestionCard } from './components/QuestionCard'
import { UiIcon, type UiIconName } from './components/UiIcon'
import type {
  AnswerValue,
  ScreenerAnswers,
  ScreenerDefinition,
  ScreenerQuestion,
} from './types/screener'
import { isQuestionVisible } from './utils/visibility'
import './App.css'

interface JourneyStep {
  label: string
  startSection: number
  endSection: number
  icon: UiIconName
  description: string
  topics: Array<{ section: number; label: string }>
  accentIcons: [UiIconName, UiIconName, UiIconName]
}

const journeySteps: JourneyStep[] = [
  {
    label: 'About you',
    startSection: 1,
    endSection: 5,
    icon: 'user-round',
    description:
      'A little about your background, education, and working life.',
    topics: [
      { section: 1, label: 'Identity' },
      { section: 2, label: 'Place' },
      { section: 3, label: 'Income' },
      { section: 4, label: 'Education' },
      { section: 5, label: 'Work' },
    ],
    accentIcons: ['map', 'graduation-cap', 'briefcase-business'],
  },
  {
    label: 'Home & finances',
    startSection: 6,
    endSection: 9,
    icon: 'house',
    description:
      'Your home, household, and the practical costs of where you live.',
    topics: [
      { section: 6, label: 'Housing' },
      { section: 7, label: 'Building' },
      { section: 8, label: 'Household' },
      { section: 9, label: 'Residence' },
    ],
    accentIcons: ['wallet-cards', 'house-heart', 'users-round'],
  },
  {
    label: 'Daily needs',
    startSection: 10,
    endSection: 16,
    icon: 'hand-heart',
    description:
      'Everyday resources and services that help life run smoothly.',
    topics: [
      { section: 10, label: 'Coverage' },
      { section: 11, label: 'Internet' },
      { section: 12, label: 'Ability' },
      { section: 13, label: 'Language' },
      { section: 14, label: 'Family' },
      { section: 15, label: 'Transport' },
      { section: 16, label: 'Needs' },
    ],
    accentIcons: ['wifi', 'bus', 'shopping-basket'],
  },
  {
    label: 'Health & wellbeing',
    startSection: 17,
    endSection: 20,
    icon: 'heart-pulse',
    description:
      'Your connections, emotional wellbeing, and everyday activity.',
    topics: [
      { section: 17, label: 'Connection' },
      { section: 18, label: 'Neighbourhood' },
      { section: 19, label: 'Wellbeing check-in' },
      { section: 20, label: 'Activity' },
    ],
    accentIcons: ['messages-square', 'clipboard-heart', 'activity'],
  },
  {
    label: 'Support & digital inclusion',
    startSection: 21,
    endSection: 22,
    icon: 'users-round',
    description:
      'Legal support and the digital conditions that shape access to care.',
    topics: [
      { section: 21, label: 'Legal needs' },
      { section: 22, label: 'Digital access & inclusion' },
    ],
    accentIcons: ['scale', 'smartphone', 'wifi'],
  },
]

const sectionPresentation: Record<
  number,
  { label: string; icon: UiIconName }
> = {
  1: { label: 'Identity', icon: 'users-round' },
  2: { label: 'Place', icon: 'map' },
  3: { label: 'Income', icon: 'wallet-cards' },
  4: { label: 'Education', icon: 'graduation-cap' },
  5: { label: 'Work', icon: 'briefcase-business' },
  6: { label: 'Housing', icon: 'house' },
  7: { label: 'Building', icon: 'building-2' },
  8: { label: 'Household', icon: 'users-round' },
  9: { label: 'Residence', icon: 'map-pinned' },
  10: { label: 'Health coverage', icon: 'shield-plus' },
  11: { label: 'Internet access', icon: 'wifi' },
  12: { label: 'Everyday ability', icon: 'accessibility' },
  13: { label: 'Language', icon: 'languages' },
  14: { label: 'Family', icon: 'house-heart' },
  15: { label: 'Transport', icon: 'bus' },
  16: { label: 'Unmet needs', icon: 'shopping-basket' },
  17: { label: 'Social connection', icon: 'messages-square' },
  18: { label: 'Neighbourhood support', icon: 'community-circle' },
  19: { label: 'Wellbeing check-in', icon: 'clipboard-heart' },
  20: { label: 'Physical activity', icon: 'activity' },
  21: { label: 'Legal needs', icon: 'scale' },
  22: { label: 'Digital Access and Inclusion', icon: 'smartphone' },
}

const questionIconOverrides: Record<string, UiIconName> = {
  dem_age_group: 'user-round',
  dem_gender: 'users-round',
  dem_gender_other_text: 'user-round',
  q1_ethnic_group: 'users-round',
  q1_ethnic_group_other_text: 'users-round',
  q2_europe_region: 'map',
  q2_ancestry: 'globe',
  q5b_last_worked: 'briefcase-business',
  legal_need: 'scale',
  legal_need_domains: 'scale',
  legal_need_other_text: 'scale',
  legal_support_access: 'support',
  ddoh_device_access: 'smartphone',
  ddoh_connectivity: 'wifi',
  ddoh_affordability: 'wallet-cards',
  ddoh_accessibility: 'accessibility',
  ddoh_support: 'support',
  ddoh_privacy_trust: 'lock',
}

function getQuestionIcon(question: ScreenerQuestion): UiIconName {
  return (
    questionIconOverrides[question.id] ??
    sectionPresentation[question.section]?.icon ??
    'sparkles'
  )
}

function getJourneyStepIndex(section: number) {
  const stepIndex = journeySteps.findIndex(
    (step) =>
      section >= step.startSection && section <= step.endSection,
  )

  return stepIndex === -1 ? 0 : stepIndex
}

function hasAnswer(
  question: ScreenerQuestion,
  value: AnswerValue | undefined,
) {
  if (value === undefined || value === '') {
    return false
  }

  if (Array.isArray(value)) {
    return value.length > 0
  }

  if (typeof value === 'object' && value !== null) {
    if (question.type === 'checklist') {
      if (
        question.exclusive_item_id &&
        value[question.exclusive_item_id] === true
      ) {
        return true
      }

      return (
        question.items?.every((item) => item.id in value) ??
        Object.keys(value).length > 0
      )
    }

    if (question.type === 'matrix') {
      return (
        question.rows?.every((row) => row.id in value) ??
        Object.keys(value).length > 0
      )
    }

    return Object.keys(value).length > 0
  }

  return true
}

function isOptionalQuestion(question: ScreenerQuestion) {
  return question.required === false
}

function validateQuestion(
  question: ScreenerQuestion,
  value: AnswerValue | undefined,
) {
  const questionLabel = `“${question.text}”`

  if (!isOptionalQuestion(question) && !hasAnswer(question, value)) {
    return `Please answer ${questionLabel} before continuing.`
  }

  if (value === undefined || value === '') {
    return null
  }

  if (question.type === 'integer') {
    if (typeof value !== 'number' || !Number.isInteger(value)) {
      return `Please enter a whole number for ${questionLabel}.`
    }
  }

  if (question.type === 'currency') {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      return `Please enter a valid amount for ${questionLabel}.`
    }
  }

  if (typeof value === 'number') {
    if (question.min !== undefined && value < question.min) {
      return `The minimum value for ${questionLabel} is ${question.min}.`
    }

    if (question.max !== undefined && value > question.max) {
      return `The maximum value for ${questionLabel} is ${question.max}.`
    }
  }

  if (
    question.type === 'text' &&
    question.pattern &&
    typeof value === 'string'
  ) {
    try {
      if (!new RegExp(question.pattern).test(value)) {
        return `Please check the format of your answer for ${questionLabel}.`
      }
    } catch {
      return `The validation rule for ${questionLabel} is invalid.`
    }
  }

  return null
}

function App() {
  const [screener, setScreener] =
    useState<ScreenerDefinition | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [answers, setAnswers] = useState<ScreenerAnswers>({})
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isCheckingSection, setIsCheckingSection] =
    useState(false)
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
      <main className="status-page">
        <section className="status-panel" role="alert">
          <span className="status-icon status-icon-error">!</span>
          <p className="eyebrow">Connection problem</p>
          <h1>Unable to load the assessment</h1>
          <p>{error}</p>
        </section>
      </main>
    )
  }

  if (!screener) {
    return (
      <main className="status-page" aria-busy="true">
        <section className="status-panel">
          <span className="loading-mark" aria-hidden="true" />
          <p className="eyebrow">HEALIE</p>
          <h1>Loading your assessment…</h1>
        </section>
      </main>
    )
  }

  const questions = screener.questions
  const sections = Array.from(
    new Set(questions.map((question) => question.section)),
  )
  const currentSection = sections[currentSectionIndex]
  const currentJourneyStepIndex = getJourneyStepIndex(currentSection)
  const currentJourneyStep = journeySteps[currentJourneyStepIndex]
  const currentSectionPresentation = sectionPresentation[
    currentSection
  ] ?? {
    label: `Section ${currentSection}`,
    icon: 'sparkles' as UiIconName,
  }
  const visibleQuestions = questions.filter(
    (question) =>
      question.section === currentSection &&
      isQuestionVisible(question.visible_if, answers),
  )
  const isFirstSection = currentSectionIndex === 0
  const isLastSection = currentSectionIndex === sections.length - 1
  const progressValue = Math.round(
    ((currentSectionIndex + 1) / sections.length) * 100,
  )
  const answerCount = Object.keys(answers).length
  const hasSingleQuestion = visibleQuestions.length === 1
  const pageTitle = hasSingleQuestion
    ? visibleQuestions[0].text
    : currentSectionPresentation.label

  function handleAnswerChange(
    questionId: string,
    value: AnswerValue,
  ) {
    setSubmissionMessage(null)
    setSubmissionSucceeded(false)

    setAnswers((currentAnswers) => {
      const updatedAnswers: ScreenerAnswers = {
        ...currentAnswers,
      }

      if (value === '') {
        delete updatedAnswers[questionId]
      } else {
        updatedAnswers[questionId] = value
      }

      for (const question of questions) {
        if (!isQuestionVisible(question.visible_if, updatedAnswers)) {
          delete updatedAnswers[question.id]
        }
      }

      return updatedAnswers
    })
  }

  async function handleSubmit() {
    const sectionError = visibleQuestions
      .map((question) =>
        validateQuestion(question, answers[question.id]),
      )
      .find((message) => message !== null)

    if (sectionError) {
      setSubmissionMessage(sectionError)
      return
    }

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

  async function handleContinue() {
    const sectionError = visibleQuestions
      .map((question) =>
        validateQuestion(question, answers[question.id]),
      )
      .find((message) => message !== null)

    if (sectionError) {
      setSubmissionMessage(sectionError)
      return
    }

    setIsCheckingSection(true)
    setSubmissionMessage(null)

    try {
      const result = await validateScreener(
        answers,
        currentSection,
      )

      if (!result.valid) {
        setSubmissionMessage(result.message)
        return
      }

      changeSection(currentSectionIndex + 1)
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : 'An unexpected error occurred.'

      setSubmissionMessage(message)
    } finally {
      setIsCheckingSection(false)
    }
  }

  function changeSection(nextIndex: number) {
    setCurrentSectionIndex(nextIndex)

    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function handleStartAgain() {
    setAnswers({})
    setCurrentSectionIndex(0)
    setSubmissionMessage(null)
    setSubmissionSucceeded(false)

    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (submissionSucceeded) {
    return (
      <main className="completion-page">
        <section
          className="completion-panel"
          aria-labelledby="completion-heading"
        >
          <div className="completion-brand" aria-label="HEALIE"><span className="official-logo-mark" aria-hidden="true">
  <img
    src="/healie_final_official_logo_trans_crop.png"
    alt=""
  />
</span>
            <span className="healie-wordmark">Healie</span>
          </div>

          <span className="completion-check" aria-hidden="true">
            <UiIcon name="check" />
          </span>
          <p className="eyebrow">Assessment complete</p>
          <h1 id="completion-heading">Thank you</h1>
          <p>Your responses were checked successfully.</p>
          <p className="completion-note">
            This research prototype does not save your responses yet.
          </p>
          <button
            className="button button-primary"
            type="button"
            onClick={handleStartAgain}
          >
            Start again
            <UiIcon name="arrow-right" />
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="screener-shell">
      <aside className="assessment-sidebar">
        <div className="sidebar-brand" aria-label="HEALIE">
          <img
            className="sidebar-logo"
            src="/healie_final_official_logo_full.png"
            alt="Healie"
          />
          <p className="sidebar-subtitle">
            Social and digital factors affecting health
          </p>
        </div>

        <div className="sidebar-progress">
          <div>
            <strong>
              Section {currentSectionIndex + 1} of {sections.length}
            </strong>
            <span>{progressValue}% complete</span>
          </div>
          <div
            className="sidebar-progress-track"
            role="progressbar"
            aria-label="Assessment progress"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progressValue}
          >
            <span style={{ width: `${progressValue}%` }} />
          </div>
        </div>

        <nav className="sidebar-journey" aria-label="Assessment journey">
          <ol>
            {journeySteps.map((step, index) => {
              const isComplete = index < currentJourneyStepIndex
              const isActive = index === currentJourneyStepIndex

              return (
                <li
                  className={[
                    'sidebar-step',
                    isComplete ? 'is-complete' : '',
                    isActive ? 'is-active' : '',
                  ]
                    .filter(Boolean)
                    .join(' ')}
                  key={step.label}
                  aria-current={isActive ? 'step' : undefined}
                >
                  <div className="sidebar-step-heading">
                    <span className="sidebar-step-icon" aria-hidden="true">
                      {isComplete ? (
                        <UiIcon name="check" />
                      ) : (
                        <UiIcon name={step.icon} />
                      )}
                    </span>
                    <span>{step.label}</span>
                  </div>

                  {isActive && (
                    <ol className="sidebar-topics">
                      {step.topics.map((topic) => (
                        <li
                          className={[
                            topic.section < currentSection
                              ? 'is-complete'
                              : '',
                            topic.section === currentSection
                              ? 'is-active'
                              : '',
                          ]
                            .filter(Boolean)
                            .join(' ')}
                          key={topic.section}
                        >
                          {topic.label}
                        </li>
                      ))}
                    </ol>
                  )}
                </li>
              )
            })}
          </ol>
        </nav>

        <p className="sidebar-privacy">
          <UiIcon name="lock" />
          Your answers remain in this browser during this research
          prototype.
        </p>

        <div className="sidebar-project-footer">
          <strong>HEALIE research prototype</strong>
          <span>
            Christina Kakalou ·{' '}
            <a
              href="https://ckakalou.github.io"
              target="_blank"
              rel="noreferrer"
            >
              ckakalou.github.io
            </a>
          </span>
        </div>
      </aside>

      <section className="screener-main">
        <header className="section-context">
          <div>
            <p>
              Part {currentJourneyStepIndex + 1} of {journeySteps.length}
            </p>
            <strong>{currentJourneyStep.label}</strong>
            <span>{currentJourneyStep.description}</span>
          </div>
          <span className="section-context-icon" aria-hidden="true">
            <UiIcon name={currentJourneyStep.icon} />
          </span>
        </header>

        <div className="screener-content">
          <section
            className="question-column"
            aria-labelledby="section-heading"
          >
            <p className="section-number">
              Section {currentSectionIndex + 1} of {sections.length}
            </p>
            <div className="question-heading-row">
              <span className="question-heading-icon" aria-hidden="true">
                <UiIcon name={currentSectionPresentation.icon} />
              </span>
              <h2 id="section-heading">{pageTitle}</h2>
            </div>
            <p className="section-help">
              {hasSingleQuestion
                ? 'Choose the answer that best describes your situation. You can change it before submitting.'
                : 'Complete the questions below. You can change your answers before submitting.'}
            </p>

            <div className="question-list">
              {visibleQuestions.length > 0 ? (
                visibleQuestions.map((question) => (
                  <QuestionCard
                    key={question.id}
                    question={question}
                    value={answers[question.id]}
                    onChange={handleAnswerChange}
                    hideQuestionText={hasSingleQuestion}
                    icon={getQuestionIcon(question)}
                  />
                ))
              ) : (
                <p className="empty-section">
                  No questions are available in this section.
                </p>
              )}
            </div>
          </section>
        </div>

        <footer className="screener-footer">
          <span className="answer-status" aria-live="polite">
            {answerCount} {answerCount === 1 ? 'answer' : 'answers'} recorded
          </span>

          <nav
            className="navigation-actions"
            aria-label="Assessment section navigation"
          >
            <button
              className="button button-secondary"
              type="button"
              disabled={isFirstSection}
              onClick={() => changeSection(currentSectionIndex - 1)}
            >
              <UiIcon name="arrow-left" />
              Previous
            </button>

            {isLastSection ? (
              <button
                className="button button-primary"
                type="button"
                disabled={isSubmitting}
                onClick={handleSubmit}
              >
                {isSubmitting ? 'Submitting…' : 'Submit answers'}
                {!isSubmitting && <UiIcon name="check" />}
              </button>
            ) : (
              <button
                className="button button-primary"
                type="button"
                disabled={isCheckingSection}
                onClick={handleContinue}
              >
                {isCheckingSection ? 'Checking…' : 'Continue'}
                {!isCheckingSection && <UiIcon name="arrow-right" />}
              </button>
            )}
          </nav>
        </footer>

        {submissionMessage && (
          <p className="submission-message" role="alert">
            {submissionMessage}
          </p>
        )}

        {import.meta.env.DEV && (
          <details className="development-state">
            <summary>Development: current answer state</summary>
            <pre>{JSON.stringify(answers, null, 2)}</pre>
          </details>
        )}
      </section>
    </main>
  )
}

export default App
