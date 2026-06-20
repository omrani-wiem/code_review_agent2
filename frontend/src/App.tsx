import { useState } from 'react'
import Header from './components/Header'
import CodePanel from './components/codePanel'
import ResultPanel from './components/ResultPanel'
import type { Language, TabKey, TabState, ReviewResponse } from './types'
import styles from './App.module.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const INITIAL_TABS: Record<TabKey, TabState> = {
  bugs:      { status: 'idle', content: '' },
  review:    { status: 'idle', content: '' },
  corrected: { status: 'idle', content: '' },
  tests:     { status: 'idle', content: '' },
}

const LOADING_TABS: Record<TabKey, TabState> = {
  bugs:      { status: 'loading', content: '' },
  review:    { status: 'loading', content: '' },
  corrected: { status: 'loading', content: '' },
  tests:     { status: 'loading', content: '' },
}

export default function App() {
  const [loading, setLoading] = useState(false)
  const [tabs, setTabs] = useState<Record<TabKey, TabState>>(INITIAL_TABS)
  const [statusMsg, setStatusMsg] = useState<string>('')

  const handleReview = async (code: string, language: Language) => {
    setLoading(true)
    setTabs(LOADING_TABS)
    setStatusMsg(' Soumission du job...')

    const baseUrl = API_URL
    const headers = {
      'Content-Type': 'application/json',
      'X-API-Key': 'dev',
    }

    try {
      
      const submitResp = await fetch(`${baseUrl}/review/async`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ code, language }),
      })

      if (!submitResp.ok) {
        const err = await submitResp.json().catch(() => ({ detail: submitResp.statusText }))
        throw new Error(err.detail || 'Erreur lors de la soumission')
      }

      const { job_id } = await submitResp.json()
      setStatusMsg(` Job soumis (${job_id.slice(0, 8)}...) — pipeline en cours...`)

    
      await new Promise<void>((resolve, reject) => {
        let attempts = 0
        const MAX_ATTEMPTS = 80  

        const interval = setInterval(async () => {
          attempts++

          try {
            const statusResp = await fetch(`${baseUrl}/review/status/${job_id}`, { headers })
            const data = await statusResp.json()

            if (data.status === 'running') {
              setStatusMsg(` Agents en cours... (${attempts * 3}s)`)
            }

            if (data.status === 'done') {
              clearInterval(interval)
              const result: ReviewResponse = data.result
              setTabs({
                bugs:      { status: 'done', content: result.bugs || '(No output)' },
                review:    { status: 'done', content: result.review || '(No output)' },
                corrected: { status: 'done', content: result.corrected_code || '(No output)' },
                tests:     { status: 'done', content: result.tests || '(No output)' },
              })
              setStatusMsg(' Review terminée !')
              resolve()
            }

            if (data.status === 'error') {
              clearInterval(interval)
              reject(new Error(data.error || 'Erreur pipeline'))
            }

            if (attempts >= MAX_ATTEMPTS) {
              clearInterval(interval)
              reject(new Error('Timeout : le pipeline a pris trop de temps'))
            }

          } catch (err) {
            clearInterval(interval)
            reject(err)
          }
        }, 3000)
      })

    } catch (err) {
      const msg = ` ${err instanceof Error ? err.message : 'Erreur inconnue'}`
      setTabs({
        bugs:      { status: 'error', content: msg },
        review:    { status: 'error', content: msg },
        corrected: { status: 'error', content: msg },
        tests:     { status: 'error', content: msg },
      })
      setStatusMsg(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.app}>
      <Header />
      {statusMsg && (
        <div className={styles.statusBar}>
          {statusMsg}
        </div>
      )}
      <main className={styles.main}>
        <CodePanel onReview={handleReview} loading={loading} />
        <ResultPanel tabs={tabs} />
      </main>
    </div>
  )
}