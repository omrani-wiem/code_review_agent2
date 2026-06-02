import { useState } from 'react';
import type { Language } from '../types'
import styles from './codePanel.module.css';

interface Props {
    onReview: (code: string, language: Language, apiURl: string) => void
    loading: boolean
}


const LANGUAGES: { value: Language; label: string }[] = [
    { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'cpp', label: 'C++' },
  { value: 'other', label: 'Other' },
]



export default function CodePaneel({ onReview, loading }: Props) {
    const [code, setCode] = useState('')
    const [language, setLanguage] = useState<Language>('python')
    const [apiUrl, setApiURl] = useState('http://localhost:8000')

    const handleClick = ()  => {
        if (!code.trim()) {
            alert('Please paste some code fisrt.')
            return
        }
        onReview(code, language, apiUrl)
        }

        return (
            <div className={styles.panel}>
                <div className={styles.panelHeader}>
                    <h2>Input Code</h2>
                    <select
                       className={styles.langSelect}
                       value={language}
                       onChange={e => setLanguage(e.target.value as Language)}
                       >
                        {LANGUAGES.map(l => (
                            <option key={l.value} value={l.value}>
                                {l.label}
                            </option>
                        ))}
                       </select>
                       </div>
                      
                      <textarea
                        className={styles.codeInput}
                        value={code}
                        onChange={e => setCode(e.target.value)}
                        placeholder="Paste your code here..."
                        spellCheck={false}
                        />

                        <div className={styles.panelFooter}>
                            <input
                                className={styles.apiUrl}
                                type="text"
                                value={apiUrl}
                                onChange={e => setApiURl(e.target.value)}
                                placeholder="API URL"
                                /> 

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
        );

    }
  
  
