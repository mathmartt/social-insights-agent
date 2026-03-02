import { useState } from 'react'
import { IoDownloadOutline, IoDocumentOutline } from 'react-icons/io5'
import InsightHeader from './InsightHeader.jsx'
import SentimentSummary from './SentimentSummary.jsx'
import WrittenSummary from './WrittenSummary.jsx'
import ActionItems from './ActionItems.jsx'
import CommentEvidence from './CommentEvidence.jsx'
import ReasoningPanel from './ReasoningPanel.jsx'
import FollowUpChat from './FollowUpChat.jsx'
import { exportPptx, exportCsv } from '../api.js'

export default function ResultsPage({ results, query }) {
  const [exporting, setExporting] = useState(null) // 'pptx' | 'csv' | null

  async function handleExport(type) {
    setExporting(type)
    try {
      if (type === 'pptx') await exportPptx(results)
      else await exportCsv(results)
    } catch (err) {
      alert(`Export failed: ${err.message}`)
    } finally {
      setExporting(null)
    }
  }

  return (
    <main className="results-page fade-in">

      {/* Insight header */}
      <InsightHeader query={query} results={results} />

      {/* Sentiment summary with charts */}
      <SentimentSummary
        sentiment={results.sentiment_breakdown}
        trend={results.sentiment_trend}
        platformBreakdown={results.platform_breakdown}
      />

      {/* Written synthesis */}
      <WrittenSummary
        summary={results.written_summary}
        themes={results.key_themes}
      />

      {/* Action items */}
      <ActionItems items={results.action_items} />

      {/* Comment evidence */}
      <CommentEvidence comments={results.relevant_comments || []} />

      {/* Reasoning panel */}
      <ReasoningPanel
        reasoning={results.reasoning_plain}
        thinking={results.thinking}
      />

      {/* Export bar */}
      <div className="export-bar">
        <span className="export-bar__label">
          Export this analysis
        </span>
        <div className="export-bar__btns">
          <button
            className="export-btn"
            onClick={() => handleExport('pptx')}
            disabled={!!exporting}
          >
            <IoDocumentOutline size={15} />
            {exporting === 'pptx' ? 'Generating…' : 'PowerPoint (.pptx)'}
          </button>
          <button
            className="export-btn"
            onClick={() => handleExport('csv')}
            disabled={!!exporting}
          >
            <IoDownloadOutline size={15} />
            {exporting === 'csv' ? 'Exporting…' : 'Comments (.csv)'}
          </button>
        </div>
      </div>

      {/* Follow-up chat */}
      <FollowUpChat currentResults={results} />

    </main>
  )
}
