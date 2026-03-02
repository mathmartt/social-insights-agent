const PRIORITY_ICONS = { high: '💡', medium: '📌', low: '📝' }

export default function ActionItems({ items }) {
  if (!items?.length) return null

  return (
    <div className="card fade-in">
      <div className="card__title">Recommended Actions</div>
      {items.map((item, i) => {
        const priority = item.priority?.toLowerCase() || 'medium'
        return (
          <div key={i} className="action-item">
            <div className={`action-item__icon action-item__icon--${priority}`}>
              {PRIORITY_ICONS[priority] || '💡'}
            </div>
            <div className="action-item__body">
              <div className="action-item__title">{item.title}</div>
              <div className="action-item__desc">{item.description}</div>
              <div className="action-item__meta">
                <span className={`priority-badge priority-badge--${priority}`}>
                  {priority.charAt(0).toUpperCase() + priority.slice(1)} priority
                </span>
                {item.platform && (
                  <span className="platform-badge">
                    {item.platform}
                  </span>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
