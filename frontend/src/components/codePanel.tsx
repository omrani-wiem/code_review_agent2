import { useState, useCallback, useEffect } from 'react'
import type { Language } from '../types'
import styles from './CodePanel.module.css'

interface Props {
  onReview: (code: string, language: Language) => void
  loading: boolean
}

const LANGUAGES: { value: Language; label: string }[] = [
  { value: 'python',     label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java',       label: 'Java' },
  { value: 'go',         label: 'Go' },
  { value: 'rust',       label: 'Rust' },
  { value: 'cpp',        label: 'C++' },
  { value: 'other',      label: 'Other' },
]

const STORAGE_KEY = 'code_review_draft'

export default function CodePanel({ onReview, loading }: Props) {
  
  const [code, setCode]       = useState('')
  const [language, setLanguage] = useState<Language>('python')
  const [error, setError]     = useState<string | null>(null)


  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) setCode(saved)
  }, [])

  
  const handleCodeChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setCode(value)
    localStorage.setItem(STORAGE_KEY, value)   
    if (error) setError(null)                  
  }, [error])

  
  const handleClick = useCallback(() => {

    if (!code.trim()) {
      setError('Please paste some code first.')   
      return
    }
  
    onReview(code, language)
  }, [code, language, onReview])        

  
  const handleClear = useCallback(() => {
    setCode('')
    setError(null)
    localStorage.removeItem(STORAGE_KEY)
  }, [])

  return (
    <div className={styles.panel}>
      {/* Header */}
      <div className={styles.panelHeader}>
        <h2>Input Code</h2>
        <select
          className={styles.langSelect}
          value={language}
          onChange={(e) => {
              const value = e.target.value

              if (LANGUAGES.some(l => l.value === value)) {
                       setLanguage(value as Language)
              }
     }}
          disabled={loading}
        >
          {LANGUAGES.map(l => (
            <option key={l.value} value={l.value}>{l.label}</option>
          ))}
        </select>
      </div>

      {/* Message d'erreur React */}
      {error && (
        <div className={styles.errorMsg} role="alert">
           {error}
        </div>
      )}

      {/* Zone de code */}
      <textarea
        className={styles.codeInput}
        value={code}
        onChange={handleCodeChange}
        placeholder="Paste your code here..."
        spellCheck={false}
        disabled={loading}
      />

      {/* Footer */}
      <div className={styles.panelFooter}>
        {/* Bouton effacer */}
        <button
          className={styles.clearBtn}
          onClick={handleClear}
          disabled={loading || !code}
          title="Clear code"
        >
          Clear
        </button>

        {/* Bouton Review */}
        <button
          className={`${styles.runBtn} ${loading ? styles.loading : ''}`}
          onClick={handleClick}
          disabled={loading}
        >
          <div className={styles.spinner} />
          {!loading && (
            <svg className={styles.btnIcon} width={15} height={15} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
          )}
          {loading ? 'Running…' : 'Review'}
        </button>
      </div>
    </div>
  )
}