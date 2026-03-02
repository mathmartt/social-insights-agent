import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Legend, Cell,
} from 'recharts'

const BLUE   = '#4285F4'
const GREEN  = '#34A853'
const RED    = '#EA4335'
const YELLOW = '#FBBC04'

function TrendChart({ data }) {
  if (!data?.length) return <p style={{ color: 'var(--text-hint)', fontSize: 13 }}>No trend data.</p>
  return (
    <ResponsiveContainer width="100%" height={160}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
        <defs>
          <linearGradient id="gPos" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={GREEN} stopOpacity={0.3} />
            <stop offset="95%" stopColor={GREEN} stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gNeg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={RED} stopOpacity={0.3} />
            <stop offset="95%" stopColor={RED} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#E8EAED" vertical={false} />
        <XAxis dataKey="period" tick={{ fontSize: 10, fill: '#9AA0A6' }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 10, fill: '#9AA0A6' }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ background: '#fff', border: '1px solid #E8EAED', borderRadius: 8, fontSize: 12 }}
          labelStyle={{ fontWeight: 600, color: '#202124' }}
        />
        <Area type="monotone" dataKey="positive" stroke={GREEN} fill="url(#gPos)" strokeWidth={2} name="Positive" />
        <Area type="monotone" dataKey="neutral"  stroke={BLUE}  fill="none"        strokeWidth={1.5} strokeDasharray="4 2" name="Neutral" />
        <Area type="monotone" dataKey="negative" stroke={RED}   fill="url(#gNeg)" strokeWidth={2} name="Negative" />
      </AreaChart>
    </ResponsiveContainer>
  )
}

function PlatformChart({ data }) {
  if (!data?.length) return <p style={{ color: 'var(--text-hint)', fontSize: 13 }}>No platform data.</p>
  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 8, bottom: 0, left: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E8EAED" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 10, fill: '#9AA0A6' }} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="platform" tick={{ fontSize: 11, fill: '#5F6368' }} tickLine={false} axisLine={false} width={58} />
        <Tooltip
          contentStyle={{ background: '#fff', border: '1px solid #E8EAED', borderRadius: 8, fontSize: 12 }}
        />
        <Bar dataKey="positive" stackId="a" fill={GREEN}  name="Positive" radius={[0,0,0,0]} />
        <Bar dataKey="neutral"  stackId="a" fill={BLUE}   name="Neutral" />
        <Bar dataKey="negative" stackId="a" fill={RED}    name="Negative" radius={[0,3,3,0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default function SentimentSummary({ sentiment, trend, platformBreakdown }) {
  const pos = sentiment?.positive_pct ?? 0
  const neu = sentiment?.neutral_pct  ?? 0
  const neg = sentiment?.negative_pct ?? 0
  const total = sentiment?.total_relevant ?? 0

  return (
    <div className="card fade-in">
      <div className="card__title">Sentiment Breakdown</div>

      {/* Big three numbers */}
      <div className="sentiment-grid">
        <div className="sentiment-stat sentiment-stat--pos">
          <div className="sentiment-stat__pct">{pos.toFixed(0)}%</div>
          <div className="sentiment-stat__label">Positive</div>
          <div className="sentiment-stat__count">{Math.round(total * pos / 100)} comments</div>
        </div>
        <div className="sentiment-stat sentiment-stat--neu">
          <div className="sentiment-stat__pct">{neu.toFixed(0)}%</div>
          <div className="sentiment-stat__label">Neutral</div>
          <div className="sentiment-stat__count">{Math.round(total * neu / 100)} comments</div>
        </div>
        <div className="sentiment-stat sentiment-stat--neg">
          <div className="sentiment-stat__pct">{neg.toFixed(0)}%</div>
          <div className="sentiment-stat__label">Negative</div>
          <div className="sentiment-stat__count">{Math.round(total * neg / 100)} comments</div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-row">
        <div>
          <p className="chart-section__title">Sentiment over time</p>
          <TrendChart data={trend} />
        </div>
        <div>
          <p className="chart-section__title">By platform</p>
          <PlatformChart data={platformBreakdown} />
        </div>
      </div>
    </div>
  )
}
