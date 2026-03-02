import { useState, useEffect, useRef } from 'react'
import { IoSearchOutline } from 'react-icons/io5'
import { getDataInfo } from '../api.js'

const SUGGESTIONS = [
  "What are users saying about Pixel camera quality in Brazil?",
  "How is Android Theft Detection being received?",
  "What do users think about Gemini AI on Android?",
  "Show me negative feedback about battery life",
]

export default function SearchPage({ onSearch }) {
  const [query, setQuery] = useState('')
  const [dataInfo, setDataInfo] = useState(null)
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
    getDataInfo().then(setDataInfo).catch(() => {})
  }, [])

  function submit(q) {
    const text = q ?? query
    if (text.trim()) onSearch(text.trim())
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <main className="search-page fade-in">
      <p className="search-page__eyebrow">Google Marketing Intelligence</p>

      <h1 className="search-page__headline">
        What are your users<br />saying right now?
      </h1>
      <p className="search-page__subhead">
        Ask anything about your owned social data —<br />
        get a <span>trusted, evidence-backed answer</span> in seconds.
      </p>

      {/* Search bar */}
      <div className="search-bar">
        <input
          ref={inputRef}
          className="search-bar__input"
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What are users saying about Pixel camera quality in Brazil?"
          autoComplete="off"
        />
        <button
          className="search-bar__btn"
          onClick={() => submit()}
          disabled={!query.trim()}
          title="Search"
        >
          <IoSearchOutline size={18} />
        </button>
      </div>

      {/* Suggestion chips */}
      <div className="suggestion-chips">
        {SUGGESTIONS.map(s => (
          <button key={s} className="chip" onClick={() => submit(s)}>
            {s}
          </button>
        ))}
      </div>

      {/* Data pill */}
      {dataInfo?.loaded && (
        <div className="data-pill">
          <span>●</span>
          <strong>{dataInfo.total_rows.toLocaleString()}</strong> comments loaded ·{' '}
          {dataInfo.date_range?.start} → {dataInfo.date_range?.end}
        </div>
      )}
    </main>
  )
}
