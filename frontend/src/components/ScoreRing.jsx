import { BAND_COLOUR } from '../labels.js'

// A circular score, coloured by band. The arc animates when the value changes (morphing lens).
export default function ScoreRing({ value, band }) {
  const r = 36
  const C = 2 * Math.PI * r
  const pct = value === null ? 0 : Math.max(0, Math.min(100, value))
  const colour = BAND_COLOUR[band] || '#98a2b3'
  return (
    <div className="ring-wrap" role="img" aria-label={value === null ? 'No score yet' : `Score ${Math.round(value)} out of 100`}>
      <svg width="84" height="84" viewBox="0 0 84 84">
        <circle cx="42" cy="42" r={r} fill="none" stroke="#2b2b2b" strokeWidth="8" />
        <circle
          className="ring-arc"
          cx="42"
          cy="42"
          r={r}
          fill="none"
          stroke={colour}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={C}
          strokeDashoffset={C * (1 - pct / 100)}
        />
      </svg>
      <div className="ring-num" style={{ color: colour }}>
        {value === null ? '—' : Math.round(value)}
      </div>
    </div>
  )
}
