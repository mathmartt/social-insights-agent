import { useState } from 'react'
import { IoChevronDown, IoFlaskOutline } from 'react-icons/io5'

export default function ReasoningPanel({ reasoning, thinking }) {
  const [open, setOpen] = useState(false)
  const [showThinking, setShowThinking] = useState(false)

  if (!reasoning && !thinking) return null

  return (
    <div className="reasoning-panel fade-in">
      <button className="reasoning-panel__toggle" onClick={() => setOpen(v => !v)}>
        <div className="reasoning-panel__toggle-left">
          <IoFlaskOutline size={16} className="reasoning-panel__icon" />
          <span>Analysis Reasoning</span>
          <span style={{ fontSize: 12, color: 'var(--text-hint)', marginLeft: 4 }}>
            — how the agent reached these conclusions
          </span>
        </div>
        <IoChevronDown
          size={16}
          className={`reasoning-panel__chevron${open ? ' open' : ''}`}
        />
      </button>

      {open && (
        <div className="reasoning-panel__body">
          {reasoning && (
            <p className="reasoning-panel__text">{reasoning}</p>
          )}

          {thinking && (
            <div style={{ marginTop: reasoning ? 16 : 0 }}>
              <button
                style={{
                  fontSize: 12, color: 'var(--blue)', fontWeight: 500,
                  background: 'none', border: 'none', cursor: 'pointer', padding: 0,
                  marginBottom: 8,
                }}
                onClick={() => setShowThinking(v => !v)}
              >
                {showThinking ? '▼ Hide' : '▶ Show'} extended thinking chain
              </button>

              {showThinking && (
                <div className="reasoning-panel__thinking">
                  <div className="reasoning-panel__thinking-label">
                    Claude's Extended Thinking
                  </div>
                  <div className="reasoning-panel__thinking-text">{thinking}</div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
