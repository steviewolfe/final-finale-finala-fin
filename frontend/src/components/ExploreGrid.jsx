import { useState } from 'react'
import { niceCategory } from '../labels.js'

// Explore: every quoted claim as a dot, grouped by category. Dot size follows the active profile's weight.
const ORDER = [
  'schedule_flexibility',
  'remote_policy',
  'communication_style',
  'pace_and_pressure',
  'work_environment',
  'interview_process',
  'caregiving_and_leave',
  'role_clarity',
]
const SIGNAL = {
  negative: { label: 'Restriction', colour: 'var(--pink)' },
  unclear: { label: 'Unclear', colour: 'var(--teal)' },
  positive: { label: 'Benefit', colour: 'var(--mustard)' },
}

export default function ExploreGrid({ result, lens, selectedId, onSelect }) {
  const [on, setOn] = useState({ negative: true, unclear: true, positive: true })
  const impactFor = (e) => e.impact.find((x) => x.profile_id === lens) || e.impact[0]
  const hasEvidence = new Set(result.evidence.map((e) => e.category))

  return (
    <section className="explore" aria-label="Explore all evidence">
      <div className="explore-head">
        <h3>Explore the whole posting</h3>
        <p className="hint">
          Each dot is one quoted claim. Bigger dots weigh more for this profile. &ldquo;Not mentioned&rdquo; marks an
          area the posting does not cover.
        </p>
        <div className="signal-toggles" role="group" aria-label="Show signals">
          {Object.entries(SIGNAL).map(([key, s]) => (
            <button key={key} aria-pressed={on[key]} onClick={() => setOn((v) => ({ ...v, [key]: !v[key] }))}>
              <span className="swatch" style={{ background: s.colour }} aria-hidden="true" />
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {ORDER.map((cat) => {
        const items = result.evidence.filter((e) => e.category === cat && on[e.signal])
        const none = !hasEvidence.has(cat)
        return (
          <div className="explore-row" key={cat}>
            <span className="explore-label">{niceCategory(cat)}</span>
            <div className="dots">
              {items.map((e) => {
                const weight = impactFor(e)?.weight ?? 0
                const size = 10 + Math.round(weight * 70)
                return (
                  <button
                    key={e.id}
                    className={`dot-hit ${selectedId === e.id ? 'is-selected' : ''}`}
                    aria-label={`${SIGNAL[e.signal].label}: ${e.exact_quote}`}
                    onClick={() => onSelect(e.id)}
                  >
                    <span className="dot" style={{ width: size, height: size, background: SIGNAL[e.signal].colour }} />
                  </button>
                )
              })}
              {none && <span className="dot-empty small">Not mentioned</span>}
            </div>
          </div>
        )
      })}
    </section>
  )
}
