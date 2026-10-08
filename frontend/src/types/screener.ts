export type QuestionType =
  | 'single-select'
  | 'multi-select'
  | 'text'
  | 'boolean'
  | 'integer'
  | 'currency'
  | 'checklist'
  | 'matrix'

export type PrimitiveValue = string | number | boolean

export type StructuredAnswer = Record<string, boolean | number>

export type AnswerValue =
  | string
  | number
  | boolean
  | string[]
  | StructuredAnswer

export type ScreenerAnswers = Record<string, AnswerValue>

export interface QuestionOption {
  value: string | number
  label: string
  free_text_hint?: string
}

export interface ChecklistItem {
  id: string
  label: string
  type: 'boolean'
}

export interface MatrixRow {
  id: string
  label: string
}

export interface ScaleOption {
  value: number
  label: string
}

export interface VisibilityCondition {
  question: string
  operator: '=' | 'contains'
  value: PrimitiveValue
}

export interface VisibilityRule {
  any?: VisibilityCondition[]
  all?: VisibilityCondition[]
}

export interface ScreenerQuestion {
  id: string
  section: number
  text: string
  type: QuestionType

  required?: boolean
  placeholder?: string
  pattern?: string

  min?: number
  max?: number
  currency?: string

  options?: QuestionOption[]
  items?: ChecklistItem[]
  exclusive_item_id?: string
  exclusive_option_value?: string
  rows?: MatrixRow[]
  scale?: ScaleOption[]

  visible_if?: VisibilityRule
  allow_free_text_for_marked_options?: boolean

  scoring?: Record<string, unknown>
}

export interface ContextField {
  key: string
  type: 'integer' | 'boolean'
  required: boolean
  default?: PrimitiveValue
  description: string
}

export interface ScreenerUiSettings {
  pagination: 'sectioned'
  show_progress: boolean
  allow_skip: boolean
}

export interface ScreenerDefinition {
  title: string
  version: string
  created: string
  language: string
  notes: string[]
  context_fields: ContextField[]
  questions: ScreenerQuestion[]

  computed: Record<string, unknown>[]
  flags: Record<string, unknown>[]
  ui: ScreenerUiSettings
}

export interface ScreenerApiResponse {
  screener: ScreenerDefinition
}
export interface ScreenerValidationResult {
  valid: boolean
  message: string
  derived: Record<string, unknown>
}
