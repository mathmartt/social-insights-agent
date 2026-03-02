import { useState } from 'react'
import { IoSettingsOutline, IoArrowBack } from 'react-icons/io5'
import SearchPage from './components/SearchPage.jsx'
import ResultsPage from './components/ResultsPage.jsx'
import SettingsModal from './components/SettingsModal.jsx'
import LoadingState from './components/LoadingState.jsx'
import { queryInsights } from './api.js'

export default function App() {
  const [view, setView] = useState('search') // 'search' | 'loading' | 'results' | 'error'
  const [showSettings, setShowSettings] = useState(false)
  const [currentQuery, setCurrentQuery] = useState('')
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  async function handleSearch(query) {
    if (!query.trim()) return
    setCurrentQuery(query)
    setError(null)
    setView('loading')

    try {
      const data = await queryInsights(query)
      setResults(data)
      setView('results')
    } catch (err) {
      setError(err.message)
      setView('error')
    }
  }

  function handleNewSearch() {
    setView('search')
    setResults(null)
    setError(null)
  }

  return (
    <div className="app">
      {/* ── Top nav ─────────────────────────────────────────────────────── */}
      <nav className="topnav">
        {view !== 'search' ? (
          <button className="topnav__back-btn" onClick={handleNewSearch}>
            <IoArrowBack size={16} />
            New search
          </button>
        ) : (
          <div className="topnav__logo">
            <span className="topnav__logo-dot" style={{ background: '#4285F4' }} />
            <span className="topnav__logo-dot" style={{ background: '#EA4335' }} />
            <span className="topnav__logo-dot" style={{ background: '#FBBC04' }} />
            <span className="topnav__logo-dot" style={{ background: '#34A853' }} />
            Social Insights Agent
          </div>
        )}
        <div className="topnav__spacer" />
        <button
          className="topnav__settings-btn"
          onClick={() => setShowSettings(true)}
          title="Data Status"
        >
          <IoSettingsOutline size={20} />
        </button>
      </nav>

      {/* ── Content ──────────────────────────────────────────────────────── */}
      {view === 'search' && <SearchPage onSearch={handleSearch} />}
      {view === 'loading' && <LoadingState query={currentQuery} />}
      {view === 'results' && results && (
        <ResultsPage results={results} query={currentQuery} />
      )}
      {view === 'error' && (
        <div className="results-page">
          <div className="card error-card">
            <div className="error-card__icon">⚠️</div>
            <div className="error-card__title">Something went wrong</div>
            <div className="error-card__msg">{error}</div>
            <button className="btn-secondary" style={{ marginTop: 8 }} onClick={() => setView('search')}>
              Try again
            </button>
          </div>
        </div>
      )}

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </div>
  )
}
