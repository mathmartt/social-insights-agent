const BASE = '/api'

async function request(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const msg = body.detail || `HTTP ${res.status}`
    const err = new Error(msg)
    err.status = res.status
    throw err
  }
  return res
}

export async function queryInsights(query) {
  const res = await request('/query', {
    method: 'POST',
    body: JSON.stringify({ query }),
  })
  return res.json()
}

export async function followUp(query, conversationHistory, currentResults) {
  const res = await request('/follow-up', {
    method: 'POST',
    body: JSON.stringify({
      query,
      conversation_history: conversationHistory,
      current_results: currentResults,
    }),
  })
  return res.json()
}

export async function getDataInfo() {
  const res = await request('/data-info')
  return res.json()
}

export async function exportPptx(data) {
  const res = await request('/export/pptx', {
    method: 'POST',
    body: JSON.stringify({ data }),
  })
  const blob = await res.blob()
  _download(blob, 'social_insights_report.pptx')
}

export async function exportCsv(data) {
  const res = await request('/export/csv', {
    method: 'POST',
    body: JSON.stringify({ data }),
  })
  const blob = await res.blob()
  _download(blob, 'relevant_comments.csv')
}

function _download(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}
