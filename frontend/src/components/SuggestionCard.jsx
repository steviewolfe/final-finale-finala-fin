import { SIGNAL_NAME, niceCategory, scoreLine } from '../labels.js'

// A card for one evidence item. Selecting it highlights its underline.
export default function SuggestionCard({ item, lens, selected, pulse, cardRef, onSelect, onLocate }) {
  const impact = item.impact.find((x) => x.profile_id === lens) || item.impact[0]
  return (
    <article
      ref={cardRef}
      className={`card ${selected ? 'is-selected' : ''} ${pulse ? 'is-pulse' : ''}`}
      style={{ '--accent': `var(--${item.signal === 'negative' ? 'red-stroke' : item.signal === 'unclear' ? 'blue-stroke' : 'green-stroke'})` }}
      onClick={() => onSelect(item.id)}
    >
      <div className="row between">
        <span className={`signal signal-${item.signal}`}>{SIGNAL_NAME[item.signal]}</span>
        <span className="muted small">{niceCategory(item.category)}</span>
      </div>
      <blockquote>&ldquo;{item.exact_quote}&rdquo;</blockquote>
      <p className="why">{item.why}</p>
      {impact && <p className="impact">{scoreLine(impact, item.category)}</p>}
      <div className="actions">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onLocate(item.id)
          }}
        >
          Show in posting
        </button>
      </div>
    </article>
  )
}
