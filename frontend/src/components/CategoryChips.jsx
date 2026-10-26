import { useState } from 'react'
import { niceCategory } from '../labels.js'

// Miller's Law: show at most seven filters. The rest sit behind "More".
const VISIBLE = 7

export default function CategoryChips({ categories, counts, active, onChange }) {
  const [showAll, setShowAll] = useState(false)
  const shown = showAll ? categories : categories.slice(0, VISIBLE)
  const hidden = categories.length - shown.length

  return (
    <div className="cat-chips" role="group" aria-label="Filter by category">
      <button aria-pressed={active === null} onClick={() => onChange(null)}>
        All
      </button>
      {shown.map((c) => (
        <button key={c} aria-pressed={active === c} onClick={() => onChange(c)}>
          {niceCategory(c)}
          <span className="count">{counts[c] ?? 0}</span>
        </button>
      ))}
      {hidden > 0 && (
        <button onClick={() => setShowAll(true)}>+{hidden} more</button>
      )}
    </div>
  )
}
