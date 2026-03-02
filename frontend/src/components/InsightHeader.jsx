export default function InsightHeader({ query, results }) {
  const { total_analyzed, candidates_reviewed, sentiment_breakdown, time_range_covered } = results
  const total_relevant = sentiment_breakdown?.total_relevant ?? 0
  const range = time_range_covered || {}

  return (
    <div className="card insight-header fade-in">
      <div className="card__title">Query</div>
      <h2 className="insight-header__query">"{query}"</h2>
      <div className="insight-header__meta">
        {range.start && (
          <span className="insight-header__meta-item">
            📅 {range.start} → {range.end}
          </span>
        )}
        <span className="insight-header__badge insight-header__badge--blue">
          {(total_analyzed || 0).toLocaleString()} comments analysed
        </span>
        <span className="insight-header__badge insight-header__badge--green">
          {total_relevant.toLocaleString()} relevant found
        </span>
        {results.data_quality_note && (
          <span style={{ fontSize: 12, color: 'var(--yellow)', display: 'flex', alignItems: 'center', gap: 4 }}>
            ⚠️ {results.data_quality_note}
          </span>
        )}
      </div>
    </div>
  )
}
