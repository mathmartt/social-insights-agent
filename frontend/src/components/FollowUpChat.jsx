import { useState, useRef, useEffect } from 'react'
import { IoSend } from 'react-icons/io5'
import { followUp } from '../api.js'

function TypingIndicator() {
  return (
    <div className="chat-bubble chat-bubble--agent">
      <div className="chat-bubble__avatar">SI</div>
      <div className="chat-bubble__body">
        <div className="chat-bubble__content">
          <div className="typing-indicator">
            <span /><span /><span />
          </div>
        </div>
      </div>
    </div>
  )
}

export default function FollowUpChat({ currentResults }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function buildHistory() {
    return messages.map(m => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.text,
    }))
  }

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: 'user', text, ts: Date.now() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setError(null)
    setLoading(true)

    try {
      const result = await followUp(
        text,
        buildHistory(),
        currentResults,
      )

      const agentMsg = {
        role: 'agent',
        text: result.answer || 'No answer returned.',
        additionalInsights: result.additional_insights,
        supportingComments: result.supporting_comments || [],
        ts: Date.now(),
      }
      setMessages(prev => [...prev, agentMsg])
    } catch (err) {
      setError(err.message)
      setMessages(prev => prev.filter(m => m !== userMsg))
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Auto-resize textarea
  function handleInput(e) {
    setInput(e.target.value)
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 160) + 'px'
    }
  }

  return (
    <div className="followup-section fade-in">
      <div className="followup-divider">Follow-up</div>

      {/* Conversation thread */}
      {messages.length > 0 && (
        <div className="conversation-thread">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble chat-bubble--${msg.role}`}>
              <div className="chat-bubble__avatar">
                {msg.role === 'user' ? 'You' : 'SI'}
              </div>
              <div className="chat-bubble__body">
                <div className="chat-bubble__content">{msg.text}</div>

                {msg.additionalInsights && (
                  <div style={{ padding: '8px 0 0 4px', fontSize: 12, color: 'var(--text-secondary)' }}>
                    {msg.additionalInsights}
                  </div>
                )}

                {msg.supportingComments?.length > 0 && (
                  <div className="followup-comments">
                    {msg.supportingComments.slice(0, 3).map((c, j) => (
                      <div key={j} className="followup-comment">
                        <strong>{c.social_network} · {c.comment_sentiment}</strong>
                        {' '}— {c.comment_text?.slice(0, 120)}{c.comment_text?.length > 120 ? '…' : ''}
                      </div>
                    ))}
                  </div>
                )}

                <div className="chat-bubble__meta">
                  {new Date(msg.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}

          {loading && <TypingIndicator />}
        </div>
      )}

      {error && (
        <p style={{ color: 'var(--red)', fontSize: 13, marginBottom: 12 }}>⚠️ {error}</p>
      )}

      {/* Input */}
      <div className="followup-input-row">
        <textarea
          ref={textareaRef}
          className="followup-input"
          rows={1}
          value={input}
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask a follow-up question… e.g. 'How does this compare to last quarter?'"
          disabled={loading}
        />
        <button
          className="followup-send-btn"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          title="Send"
        >
          <IoSend size={17} />
        </button>
      </div>
    </div>
  )
}
