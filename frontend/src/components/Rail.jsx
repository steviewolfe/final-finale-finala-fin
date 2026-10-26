import { useState } from 'react'
import ScoreRing from './ScoreRing.jsx'
import CategoryChips from './CategoryChips.jsx'
import SuggestionCard from './SuggestionCard.jsx'
import GapCard from './GapCard.jsx'
import { BAND_COLOUR, niceCategory } from '../labels.js'

// Serial Position and Pareto: the most important suggestions first, the rest on request.
const SEVERITY = { negative: 0, unclear: 1, positive: 2 }
const TOP_SUGGESTIONS = 5

export default function Rail({
  result,
  lens,
  onLens,
  filter,
  onFilter,
  selectedId,
  pulseId,
  onSelectCard,
  onLocate,
  cardRefs,
  orderedIds,
  copied,
  onCopied,
  readProgress,
}) {
  const [showAllSuggestions, setShowAllSuggestions] = useState(false)
  const score = result.scores.find((s) => s.profile_id === lens) || result.scores[0]

  // Von Restorff: the single most important red flag, if any, stands out in the header.
  const redFlag = score?.categories.find((c) => c.red_flag)

  const counts = {}
  for (const e of result.evidence) counts[e.category] = (counts[e.category] || 0) + 1
  for (const g of result.gaps) counts[g.category] = (counts[g.category] || 0) + 1
  const categories = Object.keys(counts)

  const tally = { negative: 0, unclear: 0, positive: 0 }
  for (const e of result.evidence) tally[e.signal] += 1

  const byId = Object.fromEntries(result.evidence.map((e) => [e.id, e]))
  const ordered = orderedIds
    .map((id) => byId[id])
    .filter((e) => e && (filter === null || e.category === filter))
    .sort((a, b) => SEVERITY[a.signal] - SEVERITY[b.signal])

  const suggestions = showAllSuggestions ? ordered : ordered.slice(0, TOP_SUGGESTIONS)
  const hiddenCount = ordered.length - suggestions.length

  const gaps = result.gaps.filter((g) => filter === null || g.category === filter)
  const openGaps = result.gaps.filter((g) => g.question && !copied.includes(g.category))

  const setRef = (key) => (node) => {
    if (node) cardRefs.current[key] = node
  }

  return (
    <aside className="rail" id="rail" aria-label="Suggestions">
      <div className="score-head">
        <ScoreRing value={score?.overall ?? null} band={score?.band} />
        <div className="score-text">
          <div className="band" style={{ color: BAND_COLOUR[score?.band] || 'var(--muted)' }}>
            {score?.band || 'No score yet'}
          </div>
          <div className="muted small" title="Share of this profile's weight backed by quoted evidence in the posting.">
            Evidence covers {Math.round((score?.coverage ?? 0) * 100)}% of this profile
          </div>
          {redFlag && (
            <div className="main-concern">Main concern: {niceCategory(redFlag.category)}</div>
          )}
        </div>
      </div>

      {readProgress && readProgress.seen < readProgress.total && (
        <p className="read-progress small">Reading: {readProgress.seen} of {readProgress.total} claims seen</p>
      )}

      {/* Morphing lens: these bars animate to the new profile's values when you switch. */}
      <details className="breakdown">
        <summary>Category breakdown</summary>
        {score?.categories.map((c) => (
          <div key={c.category} className="cat-bar">
            <div className="row between small">
              <span>{niceCategory(c.category)}</span>
              <span>{c.score === null ? 'not mentioned' : Math.round(c.score)}</span>
            </div>
            <div className="bar">
              <div style={{ width: `${c.score ?? 0}%` }} />
            </div>
          </div>
        ))}
      </details>

      {/* Peak-End: a clear summary first, so the reader knows what they are looking at. */}
      <p className="summary small">
        {tally.negative} {tally.negative === 1 ? 'restriction' : 'restrictions'}, {tally.unclear} vague,{' '}
        {tally.positive} {tally.positive === 1 ? 'benefit' : 'benefits'} found.
        {result.gaps.length > 0 && ` ${result.gaps.length} ${result.gaps.length === 1 ? 'area' : 'areas'} to ask about.`}
      </p>

      <div className="lens" role="group" aria-label="Score for profile">
        {result.scores.map((s) => (
          <button key={s.profile_id} aria-pressed={lens === s.profile_id} onClick={() => onLens(s.profile_id)}>
            {s.label.split(' or ')[0]}
          </button>
        ))}
      </div>

      <CategoryChips categories={categories} counts={counts} active={filter} onChange={onFilter} />

      {/* Common Region: each group sits inside its own bounded area. */}
      {suggestions.length > 0 && (
        <section className="group" aria-label="Suggestions">
          <div className="section-title">Suggestions</div>
          {suggestions.map((item) => (
            <SuggestionCard
              key={item.id}
              item={item}
              lens={lens}
              selected={selectedId === item.id}
              pulse={pulseId === item.id}
              cardRef={setRef(`e${item.id}`)}
              onSelect={onSelectCard}
              onLocate={onLocate}
            />
          ))}
          {hiddenCount > 0 && (
            <button className="more-btn" onClick={() => setShowAllSuggestions(true)}>
              Show {hiddenCount} more
            </button>
          )}
        </section>
      )}

      {gaps.length > 0 && (
        <section className="group" aria-label="Ask about">
          <div className="section-title">
            Ask about
            {openGaps.length > 0 && <span className="muted"> · {openGaps.length} open</span>}
          </div>
          {gaps.map((gap) => (
            <GapCard
              key={gap.category}
              gap={gap}
              copied={copied.includes(gap.category)}
              onCopied={onCopied}
              cardRef={setRef(`g${gap.category}`)}
            />
          ))}
        </section>
      )}

      {result.gaps.some((g) => g.question) && openGaps.length === 0 && (
        <p className="done-line small">All questions copied. Good luck with the conversation.</p>
      )}

      {/* Peak-End Rule: every review finishes on a clear next step. */}
      <p className="rail-end small">
        Copy the questions you want to ask, then check another posting when you are ready.
      </p>

      {suggestions.length === 0 && gaps.length === 0 && (
        <p className="muted small">Nothing in this category.</p>
      )}
    </aside>
  )
}
