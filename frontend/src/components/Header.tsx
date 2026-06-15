import styles from './Header.module.css'

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width={18} height={18} fill="white">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
        </svg>
      </div>
      <h1>CrewAI Code Review</h1>
      <span className={styles.badge}>4 Agents</span>
    </header>
  )
}
