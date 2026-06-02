export type Language = 'python' | 'javascript' | 'typescript' | 'java' | 'go' | 'rust' | 'cpp' | 'other'
export type TabKey = 'bugs' | 'review' | 'corrected' | 'tests'
export type TabStatus = 'idle' | 'done' | 'error'

export interface ReviewResponse {
  language: string
  bugs: string
  review: string
  corrected_code: string
  tests: string
  final_summary: string
}

export interface TabState {
  status: TabStatus
  content: string
}
