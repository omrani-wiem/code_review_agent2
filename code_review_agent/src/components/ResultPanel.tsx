import { useState } from 'react'
import type { TabKey, TabState } from '../types'
import styles from './ResultPanel.module.css'

interface Props {
  tabs: Record<TabKey, TabState>
}

const TAB_CONFIG: { key: TabKey; label: string; badge: string; badgeClass: string; icon: string; emptyMsg: string }[] = [
  {
    key: 'bugs',
    label: 'Bugs',
    badge: '🔍 Bug Detector',
    badgeClass: 'detector',
    icon: 'search',
    emptyMsg: 'Run a review to see detected bugs',
  },
  {
    key: 'review',
    label: 'Review',
    badge: '📋 Code Reviewer',
    badgeClass: 'reviewer',
    icon: 'file',
    emptyMsg: 'Run a review to see quality feedback',
  },
  {
    key: 'corrected',
    label: 'Corrected',
    badge: '⚡ Code Corrector',
    badgeClass: 'corrector',
    icon: 'check',
    emptyMsg: 'Run a review to see corrected code',
  },
  {
    key: 'tests',
    label: 'Tests',
    badge: '✅ Test Engineer',
    badgeClass: 'tester',
    icon: 'checkbox',
    emptyMsg: 'Run a review to see generated tests',
  },
]

function EmptyIcon({ type }: { type: string }) {
  if (type === 'search') return (
    <svg width={48} height={48} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
  )
  if (type === 'file') return (
    <svg width={48} height={48} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
  )
  if (type === 'check') return (
    <svg width={48} height={48} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  )
  return (
    <svg width={48} height={48} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <polyline points="9 11 12 14 22 4"/>
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
    </svg>
  )
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  return (
    <button className={styles.copyBtn} onClick={handleCopy}>
      {copied ? 'copied!' : 'copy'}
    </button>
  )
}

export default function ResultPanel({ tabs }: Props) {
  const [activeTab, setActiveTab] = useState<TabKey>('bugs')

  return (
    <div className={styles.panel}>
      <div className={styles.tabs}>
        {TAB_CONFIG.map(({ key, label }) => {
          const status = tabs[key].status
          return (
            <div
              key={key}
              className={`${styles.tab} ${activeTab === key ? styles.active : ''} ${status !== 'idle' ? styles[status] : ''}`}
              onClick={() => setActiveTab(key)}
            >
              <div className={styles.tabDot} />
              {label}
            </div>
          )
        })}
      </div>

      <div className={styles.content}>
        {TAB_CONFIG.map(({ key, badge, badgeClass, icon, emptyMsg }) => {
          const { status, content } = tabs[key]
          const isActive = activeTab === key
          const hasCopy = key === 'corrected' || key === 'tests'

          return (
            <div key={key} className={`${styles.tabContent} ${isActive ? styles.contentActive : ''}`}>
              {status === 'idle' ? (
                <div className={styles.emptyState}>
                  <EmptyIcon type={icon} />
                  <p>{emptyMsg}</p>
                </div>
              ) : (
                <>
                  <div className={`${styles.agentBadge} ${styles[`badge_${badgeClass}`]}`}>
                    {badge}
                  </div>
                  <div className={styles.resultSection}>
                    {hasCopy && <CopyButton text={content} />}
                    <pre>{content}</pre>
                  </div>
                </>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
