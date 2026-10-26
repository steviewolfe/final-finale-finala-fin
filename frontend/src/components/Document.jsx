import Mark from './Mark.jsx'

// Renders the posting as text with underlines. Plain segments stay plain.
// litIds: a Set of evidence ids that have been reached while reading, or null for all.
export default function Document({
  segments,
  items,
  lens,
  visibleIds,
  litIds,
  selectedId,
  pulseId,
  onSelect,
  registerMark,
  onLocateCard,
}) {
  const byId = Object.fromEntries(items.map((it) => [it.id, it]))

  return (
    <div className="paper">
      {segments.map((seg, i) => {
        if (seg.kind === 'plain') return <span key={i}>{seg.text}</span>

        // Under a category filter, hide underlines whose items are filtered out.
        const shown = seg.kind === 'flagged' || seg.ids.some((id) => visibleIds.has(id))
        if (!shown) return <span key={i}>{seg.text}</span>

        const segItems = seg.ids.filter((id) => visibleIds.has(id)).map((id) => byId[id])
        const lit = litIds === null || seg.kind === 'flagged' || seg.ids.some((id) => litIds.has(id))
        return (
          <Mark
            key={i}
            uid={i}
            segment={seg}
            items={segItems}
            lens={lens}
            lit={lit}
            isActive={selectedId !== null && seg.ids.includes(selectedId)}
            pulse={pulseId !== null && seg.ids.includes(pulseId)}
            onSelect={onSelect}
            registerMark={registerMark}
            onLocateCard={onLocateCard}
          />
        )
      })}
    </div>
  )
}
