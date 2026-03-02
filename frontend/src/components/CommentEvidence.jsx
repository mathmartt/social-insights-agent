import { useState } from 'react'
import {
  FaInstagram, FaTiktok, FaYoutube, FaFacebook, FaXTwitter, FaReddit
} from 'react-icons/fa6'
import { SiThreads } from 'react-icons/si'
import { IoHeartOutline, IoChevronDown, IoChevronUp } from 'react-icons/io5'

const PLATFORM_ICONS = {
  Instagram: <FaInstagram color="#E1306C" />,
  TikTok:    <FaTiktok color="#010101" />,
  YouTube:   <FaYoutube color="#FF0000" />,
  Facebook:  <FaFacebook color="#1877F2" />,
  X:         <FaXTwitter color="#000" />,
  Threads:   <SiThreads color="#000" />,
  Reddit:    <FaReddit color="#FF4500" />,
}

function sentimentClass(s) {
  const v = s?.toLowerCase()
  if (v === 'positive') return 'positive'
  if (v === 'negative') return 'negative'
  return 'neutral'
}

function CommentCard({ comment }) {
  const cls = sentimentClass(comment.comment_sentiment)
  const date = String(comment.comment_date || '').slice(0, 10)
  const icon = PLATFORM_ICONS[comment.social_network] || null

  return (
    <div className={`comment-card comment-card--${cls}`}>
      <div className="comment-card__header">
        <div className="comment-card__platform">
          {icon}
          <span>{comment.social_network}</span>
        </div>
        <span className={`sentiment-badge sentiment-badge--${cls}`}>
          {comment.comment_sentiment}
        </span>
      </div>
      <p className="comment-card__text">{comment.comment_text}</p>
      <div className="comment-card__footer">
        <span>@{comment.comment_author}</span>
        <div className="comment-card__likes">
          <IoHeartOutline size={12} />
          {(comment.comment_likes || 0).toLocaleString()}
        </div>
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-hint)' }}>{date}</div>
    </div>
  )
}

export default function CommentEvidence({ comments }) {
  const [showAll, setShowAll] = useState(false)
  const visible = showAll ? comments : comments?.slice(0, 9)

  if (!comments?.length) {
    return (
      <div className="card fade-in">
        <div className="card__title">Comment Evidence</div>
        <p style={{ color: 'var(--text-hint)', fontSize: 14 }}>No relevant comments found.</p>
      </div>
    )
  }

  return (
    <div className="card fade-in">
      <div className="card__title">
        Comment Evidence · {comments.length} relevant comments
      </div>

      <div className="comment-grid">
        {visible.map((c, i) => <CommentCard key={c._id ?? i} comment={c} />)}
      </div>

      {comments.length > 9 && (
        <button className="view-all-btn" onClick={() => setShowAll(v => !v)}>
          {showAll
            ? <><IoChevronUp style={{ verticalAlign: 'middle' }} /> Show fewer comments</>
            : <><IoChevronDown style={{ verticalAlign: 'middle' }} /> View all {comments.length} matching comments</>
          }
        </button>
      )}

      {showAll && (
        <div className="comment-table-wrap" style={{ marginTop: 16 }}>
          <table className="comment-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Platform</th>
                <th>Account</th>
                <th>Sentiment</th>
                <th>Likes</th>
                <th>Comment</th>
              </tr>
            </thead>
            <tbody>
              {comments.map((c, i) => (
                <tr key={c._id ?? i}>
                  <td style={{ whiteSpace: 'nowrap' }}>{String(c.comment_date || '').slice(0, 10)}</td>
                  <td>{c.social_network}</td>
                  <td>{c.google_account}</td>
                  <td>
                    <span className={`sentiment-badge sentiment-badge--${sentimentClass(c.comment_sentiment)}`}>
                      {c.comment_sentiment}
                    </span>
                  </td>
                  <td>{(c.comment_likes || 0).toLocaleString()}</td>
                  <td style={{ maxWidth: 400 }}>{c.comment_text}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
