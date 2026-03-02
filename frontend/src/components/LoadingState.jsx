import { useState, useEffect } from 'react'

const STEPS = [
  { id: 0, icon: '📂', text: 'Reading all comments…' },
  { id: 1, icon: '🔍', text: 'Identifying relevant signal…' },
  { id: 2, icon: '🧠', text: 'Analysing sentiment patterns…' },
  { id: 3, icon: '✨', text: 'Generating insights…' },
  { id: 4, icon: '📊', text: 'Preparing your report…' },
]

export default function LoadingState({ query }) {
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    const intervals = STEPS.slice(1).map((_, i) =>
      setTimeout(() => setActiveStep(i + 1), (i + 1) * 1800)
    )
    return () => intervals.forEach(clearTimeout)
  }, [])

  return (
    <div className="loading-page fade-in">
      <div className="loading-spinner" />

      <div style={{ textAlign: 'center' }}>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 4 }}>
          Analysing your query
        </p>
        <p style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', maxWidth: 400 }}>
          "{query}"
        </p>
      </div>

      <div className="loading-steps">
        {STEPS.map(step => (
          <div
            key={step.id}
            className={`loading-step ${
              step.id === activeStep ? 'active' : step.id < activeStep ? 'done' : ''
            }`}
          >
            <span className="loading-step__icon">
              {step.id < activeStep ? '✓' : step.icon}
            </span>
            <span>{step.text}</span>
          </div>
        ))}
      </div>

      <div className="loading-bar">
        <div className="loading-bar__fill" />
      </div>

      <p style={{ fontSize: 12, color: 'var(--text-hint)', textAlign: 'center' }}>
        Gemini thinking mode enabled — reasoning carefully over your data.
        <br />This typically takes 20–40 seconds.
      </p>
    </div>
  )
}
