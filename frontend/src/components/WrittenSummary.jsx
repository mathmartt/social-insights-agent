export default function WrittenSummary({ summary, themes }) {
  return (
    <div className="card fade-in">
      <div className="card__title">Summary</div>
      <p className="written-summary__text">{summary}</p>
      {themes?.length > 0 && (
        <>
          <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-hint)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 10 }}>
            Key Themes
          </p>
          <div className="themes-row">
            {themes.map(t => (
              <span key={t} className="theme-pill">{t}</span>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
