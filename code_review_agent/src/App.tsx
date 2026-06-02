import { useState } from 'react'
import Header from './components/Header'
import CodePanel from './components/CodePanel'
import ResultPanel from './components/ResultPanel'
import type { Language, TabKey, TabState, ReviewResponse } from './types'
import styles from './App.module.css'

const INITIAL_TABS: Record<TabKey, TabState> = {
  bugs:      { status: 'idle', content: '' },
  review:    { status: 'idle', content: '' },
  corrected: { status: 'idle', content: '' },
  tests:     { status: 'idle', content: '' },
}

export default function App() {
  const [loading, setLoading] = useState(false)
  const [tabs, setTabs] = useState<Record<TabKey, TabState>>(INITIAL_TABS)

  const handleReview = async (code: string, language: Language, apiUrl: string) => {
    setLoading(true)
    setTabs(INITIAL_TABS)

    try {
      const resp = await fetch(`${apiUrl.replace(/\/$/, '')}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      })

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }))
        throw new Error(err.detail || 'Server error')
      }

      const data: ReviewResponse = await resp.json()

      setTabs({
        bugs:      { status: 'done', content: data.bugs || '(No output)' },
        review:    { status: 'done', content: data.review || '(No output)' },
        corrected: { status: 'done', content: data.corrected_code || '(No output)' },
        tests:     { status: 'done', content: data.tests || '(No output)' },
      })
    } catch (err) {
      const msg = `❌ ${err instanceof Error ? err.message : 'Unknown error'}`
      setTabs({
        bugs:      { status: 'error', content: msg },
        review:    { status: 'error', content: msg },
        corrected: { status: 'error', content: msg },
        tests:     { status: 'error', content: msg },
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.app}>
      <Header />
      <main className={styles.main}>
        <CodePanel onReview={handleReview} loading={loading} />
        <ResultPanel tabs={tabs} />
      </main>
    </div>
  )
}
